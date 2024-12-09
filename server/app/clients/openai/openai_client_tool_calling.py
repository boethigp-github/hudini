import logging
from datetime import datetime

import openai
from openai import AsyncOpenAI
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage
from server.app.models.generation_error_details import ErrorGenerationModel
from server.app.models.generation.openai_model import OpenaiModel
from typing import Optional

import json

class OpenAIClient:
    async_methods = ['fetch_completion']

    CHAT_MODELS = [
        'gpt-3.5-turbo',
        'gpt-4',
        'gpt-4-turbo',
        'gpt-3.5-turbo-16k',
        'gpt-4-0613',
        'gpt-4-turbo-2024',
        'chatgpt-4o-latest',
        'gpt-4-1106-preview',
        'gpt-4-turbo-preview',
        'gpt-4-turbo-2024-04-09',
        'gpt-3.5-turbo-0125',
        'gpt-3.5-turbo-1106',
        'gpt-4o-mini',
        'gpt-4o',
        'o1-preview',
        'o1',
    ]

    DONT_SUPPORT_SYSTEM_PROMPT = [
        'o1-preview',
        'o1',
    ]

    MODEL_CONTEXT_WINDOWS = {
        'gpt-3.5-turbo': 4096,
        'gpt-4': 8192,
        'gpt-4-turbo': 4096,
        'gpt-3.5-turbo-16k': 16000,
        'gpt-4-turbo-2024': 4096,
        'o1-preview': 128000,
        'o1': 128000,
        'o1-mini': 128000,
        'gpt-4o-mini': 128000,
        'gpt-4o': 128000,
        'chatgpt-4o-latest': 128000
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)  # For async operations
        openai.api_key = api_key  # For synchronous operations
        self.logger = self.setup_logger()

        self.logger.debug(f"OpenAIClient IN_PROGRESS with API key: {api_key[:5]}...")

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def fetch_completion(self, openai_model: OpenaiModel, prompt: str, id: str,
                               context: str, presence_penalty: Optional[float] = 0.0):
        try:
            tools = [
                {
                    "name": "get_weather",
                    "description": "Fetches the weather for a given location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string",
                                         "description": "The name of the city to fetch the weather for."},
                            "unit": {"type": "string", "enum": ["Celsius", "Fahrenheit"], "default": "Celsius"},
                        },
                        "required": ["location"],
                    },
                }
            ]

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a Toolcaller. Your task is to detect the required tools and call them with correct parameters."
                    )
                },
                {"role": "user", "content": prompt},
            ]

            self.logger.debug(f"Function call with messages: {messages}")

            stream = await self.client.chat.completions.create(
                model=openai_model.id,
                messages=messages,
                temperature=0.1,
                stream=True,
                presence_penalty=presence_penalty,
                functions=tools,
                function_call="auto",
            )

            async def async_generator():
                full_content = ""
                partial_arguments = ""  # Accumulator for function arguments
                function_name = None  # Track the function name

                async for chunk in stream:
                    self.logger.debug(f"Chunk received: {chunk}")

                    # Handle function calls
                    if hasattr(chunk.choices[0].delta, "function_call"):
                        function_call = chunk.choices[0].delta.function_call
                        if function_call:
                            if function_call.name and not function_name:
                                function_name = function_call.name
                                self.logger.debug(f"Detected function name: {function_name}")

                            if function_call.arguments:
                                partial_arguments += function_call.arguments
                                self.logger.debug(f"Accumulated arguments: {partial_arguments}")

                    # Execute tool call when ready
                    if chunk.choices[0].finish_reason == "function_call" and function_name:
                        try:
                            function_args = json.loads(partial_arguments)
                            self.logger.debug(f"Parsed arguments for {function_name}: {function_args}")

                            if function_name == "get_weather":
                                try:
                                    self.logger.debug(f"Calling {function_name} with arguments: {function_args}")
                                    # Call the get_weather function
                                    result = self.get_weather(function_args["location"])

                                    # Log and add only the result to full_content
                                    self.logger.info(f"Tool {function_name} executed successfully: {result}")
                                    full_content = result  # Replace `full_content` with the result only

                                except TypeError as e:
                                    self.logger.error(f"TypeError for tool {function_name}: {e}")
                                except Exception as e:
                                    self.logger.error(f"Error while executing tool '{function_name}': {str(e)}")

                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSONDecodeError: Invalid JSON in arguments: {partial_arguments}")
                        except Exception as e:
                            self.logger.error(f"Error while executing tool '{function_name}': {str(e)}")
                        finally:
                            partial_arguments = ""
                            function_name = None

                    # Accumulate normal content
                    if hasattr(chunk.choices[0].delta, "content"):
                        content = chunk.choices[0].delta.content
                        if content:
                            full_content += content
                            self.logger.debug(f"Content received: {content}")

                    # Skip empty content before yielding
                    if not full_content.strip():
                        self.logger.debug("Skipping empty content chunk")
                        continue

                    # Create and yield the completion
                    completion = Completion(
                        id=chunk.id,
                        choices=[Choice(
                            finish_reason=chunk.choices[0].finish_reason or "null",
                            index=chunk.choices[0].index,
                            message=Message(
                                content=full_content,
                                role=chunk.choices[0].delta.role or "assistant"
                            )
                        )],
                        created=chunk.created,
                        model=openai_model.id,
                        object=chunk.object,
                        system_fingerprint=None,
                        usage=Usage(
                            completion_tokens=len(full_content.split()),
                            prompt_tokens=len(prompt.split()),
                            total_tokens=len(full_content.split()) + len(prompt.split()),
                            ended=int(datetime.utcnow().timestamp())
                        )
                    )
                    self.logger.debug(f"Completion created: {completion}")
                    yield (SuccessGenerationModel(
                        id=id,
                        model=openai_model.id,
                        completion=completion
                    ).model_dump_json()).encode('utf-8')

            return async_generator()

        except Exception as e:
            self.logger.error(f"Error in fetch_completion: {str(e)}")
            raise

    def get_weather(self, location: str, unit: str = "Celsius") -> str:

        return f"In {location} ist es 22° {unit}."


    def hudini_character(self, today, current_time):
        hudini_text = f"""
            Du bist Igor Hudini, ein unerschrockener, verdammt cleverer Assistent ...
            Today is {today} and its: {current_time}.
        """
        return hudini_text

    def trim_context(self, context: str, max_tokens: int) -> str:
        """
        Trim the context to fit within the given max tokens.
        Prioritizes the most recent content by keeping the last tokens.
        """
        context_tokens = context.split()
        if len(context_tokens) > max_tokens:
            self.logger.debug(f"Trimming context to the last {max_tokens} tokens.")
            return " ".join(context_tokens[-max_tokens:])
        return context

    def get_available_models(self) -> list:
        """
        Fetches the list of available chat models from OpenAI using the synchronous OpenAI client.

        Returns:
            list: A list of OpenaiModel instances representing the chat models available in the OpenAI API.
        """
        try:
            response = openai.models.list()
            chat_models = [
                OpenaiModel.from_dict(model.model_dump()).model_dump()
                for model in response.data
                if model.id in self.CHAT_MODELS
            ]

            self.logger.debug(f"Retrieved {len(chat_models)} chat models from OpenAI")
            return chat_models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")

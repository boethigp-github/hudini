import logging
from datetime import datetime
import json
from typing import Optional

import openai
from openai import AsyncOpenAI
from server.app.models.generation.success_generation_model import (
    SuccessGenerationModel,
    Completion,
    Choice,
    Message,
    Usage
)
from server.app.models.generation_error_details import ErrorGenerationModel
from server.app.models.generation.openai_model import OpenaiModel


class OpenAIClient:
    async_methods = ['fetch_completion']

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)  # For async operations
        openai.api_key = api_key  # For synchronous operations
        self.logger = self.setup_logger()

        self.logger.debug(f"OpenAIClient initialized with API key: {api_key[:5]}...")

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        if not logger.handlers:
            logger.addHandler(handler)
        return logger

    def get_weather(self, location: str, date: str) -> str:
        """
        Simulate fetching weather information.
        In a real implementation, this would call an external weather API.
        """
        self.logger.debug(f"1111111111111111111111111111111111111111111111111111111111111111111")

        return f"The weather in {location} on {date} is sunny with a high of 12°C. Say hello!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"

    async def fetch_completion(
        self,
        openai_model: OpenaiModel,
        prompt: str,
        id: str,
            context: str,
        presence_penalty: Optional[float] = 0.0
    ):
        try:
            self.logger.debug(
                f"Fetching streaming completion for model: {openai_model.id} "
                f"with presence_penalty: {presence_penalty}"
            )

            # Define the functions that the model can call
            functions = [
                {
                    "name": "get_weather",
                    "description": "Provides weather information for a given location and date.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city to get the weather for"
                            },
                            "date": {
                                "type": "string",
                                "description": "The date to get the weather for (YYYY-MM-DD)"
                            }
                        },
                        "required": ["location", "date"]
                    }
                }
            ]
            context += "\n\n" + (
                "Wenn eine Funktion aufgerufen wird und eine Ausgabe zurückgibt, "
                "sollst du diese Ausgabe in deiner endgültigen Antwort an den Benutzer verwenden, "
                "ohne sie zu verändern oder zu ignorieren."
            )


            self.logger.debug(f"22222222222222222222222222222222222 {context}")

            # Start the initial request with function definitions
            stream = await self.client.chat.completions.create(
                model=openai_model.id,
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                stream=True,
                presence_penalty=presence_penalty,
                functions=functions,
                function_call="auto"
            )

            async def async_generator():
                full_content = ""
                function_name = None
                collected_arguments = ""

                async for chunk in stream:
                    delta = chunk.choices[0].delta

                    # Collect content if available
                    if delta.content is not None:
                        content = delta.content
                        full_content += content

                        # Yield the assistant's response
                        completion = self.construct_completion(
                            chunk, full_content, prompt, id, openai_model.id
                        )
                        yield completion

                    # Check for function call
                    if delta.function_call is not None:
                        if delta.function_call.name is not None:
                            function_name = delta.function_call.name
                        if delta.function_call.arguments is not None:
                            collected_arguments += delta.function_call.arguments

                # Handle the function call if one was made
                if function_name and collected_arguments:
                    # Parse the arguments
                    try:
                        arguments = json.loads(collected_arguments)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Error parsing function arguments: {e}")
                        arguments = {}

                    # Execute the function
                    if function_name == "get_weather":
                        location = arguments.get("location", "")
                        date = arguments.get("date", "")
                        result = self.get_weather(location, date)
                    else:
                        result = f"Function '{function_name}' is not implemented."

                    # Send the function's response back to the assistant
                    follow_up_messages = [
                        {"role": "system", "content": context},
                        {"role": "user", "content": prompt},
                        {
                            "role": "assistant",
                            "function_call": {
                                "name": function_name,
                                "arguments": collected_arguments
                            }
                        },
                        {
                            "role": "function",
                            "name": function_name,
                            "content": result
                        }
                    ]

                    # Get the assistant's final response
                    follow_up_stream = await self.client.chat.completions.create(
                        model=openai_model.id,
                        messages=follow_up_messages,
                        temperature=0.0,
                        stream=True,
                        presence_penalty=presence_penalty
                    )

                    # Stream the assistant's final response
                    full_content = ""
                    async for follow_up_chunk in follow_up_stream:
                        delta = follow_up_chunk.choices[0].delta

                        if delta.content is not None:
                            content = delta.content
                            full_content += content

                            # Yield the assistant's final response
                            completion = self.construct_completion(
                                follow_up_chunk, full_content, prompt, id, openai_model.id
                            )
                            yield completion

        except Exception as e:
            self.logger.error(
                f"OpenAIClient::fetch_completion_stream: Error with model "
                f"{openai_model.id}: {str(e)}"
            )

            async def error_generator(error: str):
                error_response = ErrorGenerationModel(
                    model=openai_model.id,
                    error=error
                ).model_dump_json().encode('utf-8')
                yield error_response

            return error_generator(str(e))

        return async_generator()

    def construct_completion(self, chunk, full_content, prompt, id, model_id):
        """
        Helper method to construct the Completion object and serialize it.
        """
        completion = Completion(
            id=chunk.id,
            choices=[
                Choice(
                    finish_reason=chunk.choices[0].finish_reason or "null",
                    index=chunk.choices[0].index,
                    message=Message(
                        content=full_content,
                        role=chunk.choices[0].delta.role or "assistant"
                    )
                )
            ],
            created=chunk.created,
            model=model_id,
            object=chunk.object,
            system_fingerprint=None,
            usage=Usage(
                completion_tokens=len(full_content.split()),
                prompt_tokens=len(prompt.split()),
                total_tokens=len(full_content.split()) + len(prompt.split()),
                ended=int(datetime.utcnow().timestamp())
            )
        )

        return SuccessGenerationModel(
            id=id,
            model=model_id,
            completion=completion
        ).model_dump_json().encode('utf-8')

    def get_available_models(self) -> list:
        """
        Fetches the list of available models from OpenAI using the synchronous OpenAI client.

        Returns:
            list: A list of OpenaiModel instances representing the models available in the OpenAI API.
        """
        try:
            response = openai.models.list()  # Synchronous call to fetch models
            models = [
                OpenaiModel.from_dict(model.model_dump()).model_dump()  # Use the factory method to create each model
                for model in response.data
            ]

            self.logger.debug(f"Retrieved {len(models)} models from OpenAI")
            return models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")


import logging
from datetime import datetime

import openai
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage
from server.app.models.generation.openai_model import OpenaiModel
from typing import Optional
import json

from server.app.models.model_parameter.models_parameter import ModelParameter
from server.app.utils.tool_calling_tools import get_tool_calling_tools, get_weather, get_hudini_user
from server.app.utils.hudini_utils import hudini_character


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
                               context: str,
                               presence_penalty: Optional[float] = 0.0,
                               use_tool: bool = True,
                               gripsbox_content: Optional[str] = None,
                               db: AsyncSession = None,
                               user_uuid: Optional[str] = None
                               ):
        try:
            tools = []
            if use_tool:
                tools = get_tool_calling_tools()



            # Kontext vorbereiten: Gripsbox-Inhalt und Benutzerkontext hinzufügen
            context_combined = context
            if gripsbox_content:
                context_combined += f"\n\nGripsbox Content:\n{gripsbox_content}"

            # HUDINI-Systemprompt erstellen
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            system_prompt = await hudini_character(today, current_time, db, user_uuid)
            # Remove occurrences of the system prompt from context_combined
            sanitized_context = context_combined.replace(system_prompt, "").strip()
            self.logger.debug(f"sanitized_context: {sanitized_context}")
            messages = [
                {"role": "system", "content": f"{system_prompt}\n\n{sanitized_context}"},
                {"role": "user", "content": prompt},
            ]

            # Anfrage an OpenAI senden
            stream = await self.client.chat.completions.create(
                model=openai_model.id,
                messages=messages,
                temperature=0.1 if use_tool else 1.0,
                stream=True,
                presence_penalty=presence_penalty,
                functions=tools if use_tool else None,
                function_call="auto" if use_tool else None,
            )

            async def async_generator():
                full_content = ""
                partial_arguments = ""
                function_name = None

                async for chunk in stream:


                    # Tool-Handling
                    if use_tool and hasattr(chunk.choices[0].delta, "function_call"):
                        function_call = chunk.choices[0].delta.function_call
                        if function_call:
                            if function_call.name and not function_name:
                                function_name = function_call.name
                                self.logger.debug(f"Detected function name: {function_name}")

                            if function_call.arguments:
                                partial_arguments += function_call.arguments
                                self.logger.debug(f"Accumulated arguments: {partial_arguments}")

                    # Tool-Call ausführen, wenn abgeschlossen
                    if use_tool and chunk.choices[0].finish_reason == "function_call" and function_name:
                        try:
                            function_args = json.loads(partial_arguments)
                            self.logger.debug(f"Parsed arguments for {function_name}: {function_args}")

                            if function_name == "get_weather":
                                result = get_weather(function_args["location"])
                                self.logger.info(f"Tool {function_name} executed successfully: {result}")
                                full_content = result

                            elif function_name == "get_hudini_user":
                                result = await get_hudini_user()
                                self.logger.info(f"Tool {function_name} executed successfully: {result}")
                                full_content = result
                        except Exception as e:
                            self.logger.error(f"Error while executing tool '{function_name}': {str(e)}")
                        finally:
                            partial_arguments = ""
                            function_name = None

                    # Inhalte normal anhängen (ohne Tools)
                    if hasattr(chunk.choices[0].delta, "content"):
                        content = chunk.choices[0].delta.content
                        if content:
                            full_content += content


                    # Leere Inhalte überspringen
                    if not full_content.strip():
                        continue

                    # Completion erstellen und streamen
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

                    yield (SuccessGenerationModel(
                        id=id,
                        model=openai_model.id,
                        completion=completion
                    ).model_dump_json()).encode('utf-8')

            return async_generator()

        except Exception as e:
            self.logger.error(f"Error in fetch_completion: {str(e)}")
            raise



    async def fetch_hudini_systemprompt(self, db: AsyncSession, user_uuid: str) -> Optional[str]:
        """
        Fetch the 'systemprompt' parameter value for the given user from the database.

        Args:
            db (AsyncSession): The database session.
            user_uuid (str): The UUID of the user.

        Returns:
            Optional[str]: The system prompt value, if found; otherwise, None.
        """
        try:
            result = await db.execute(
                select(ModelParameter.value)
                .filter_by(user=user_uuid, parameter="systemprompt", active=True)
            )
            systemprompt = result.scalar()

            return systemprompt
        except Exception as e:
            self.logger.error(f"Error fetching system prompt for user {user_uuid}: {str(e)}")
            return None



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

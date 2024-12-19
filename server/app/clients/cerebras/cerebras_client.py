import logging


from datetime import datetime
from cerebras.cloud.sdk import Cerebras
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, Usage
from server.app.models.generation.cerebras_model import CerebrasModel
from typing import Optional
from typing import List
from server.app.models.models.models_get_response import ModelGetResponseModel
from server.app.utils.hudini_utils import hudini_character

class CerebrasClient:
    async_methods = ['fetch_completion']

    CHAT_MODELS = [
        'llama3.1-8b',
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

    ]

    MODEL_CONTEXT_WINDOWS = {
        'llama3.1-8b': 8192,
        'llama-3.3-70b': 8192,
    }

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Cerebras(api_key=api_key)  # For async operations
        self.logger = self.setup_logger()

        self.logger.debug(f"CerebrasClient IN_PROGRESS with API key: {api_key[:5]}...")

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    import asyncio

    async def fetch_completion(self, cerebras_model: CerebrasModel, prompt: str, id: str,
                               context: str, presence_penalty: Optional[float] = 0.0,
                               gripsbox_content: Optional[str] = None, db: AsyncSession = None,
                               user_uuid: Optional[str] = None):
        try:
            # Kontext vorbereiten
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            system_prompt = await hudini_character(today, current_time, db, user_uuid)

            sanitized_context = context
            if gripsbox_content:
                sanitized_context += f"\n\nGripsbox Content:\n{gripsbox_content}"

            sanitized_context = sanitized_context.replace(system_prompt, "").strip()
            self.logger.debug(f"sanitized_context: {sanitized_context}")

            messages = [
                {"role": "system", "content": f"{system_prompt}\n\n{sanitized_context}"},
                {"role": "user", "content": prompt},
            ]

            # Anfrage an Cerebras senden (Streaming aktiviert)
            stream = self.client.chat.completions.create(
                model=cerebras_model.id,
                messages=messages,
                temperature=1.0,
                stream=True,
                presence_penalty=presence_penalty
            )

            async def async_generator():
                full_content = ""
                for chunk in stream:
                    self.logger.debug(f"Received chunk: {chunk}")
                    delta_content = chunk.choices[0].delta.content or ""
                    full_content += delta_content

                    if delta_content.strip():  # Sende nur relevante Inhalte
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
                            model=cerebras_model.id,
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
                            model=cerebras_model.id,
                            completion=completion
                        ).model_dump_json()).encode('utf-8')

            return async_generator()


        except Exception as e:
            self.logger.error(f"Error in fetch_completion: {str(e)}")
            # Create a Completion object with the error message
            completion_error = Completion(
                id="error",
                choices=[Choice(
                    finish_reason="error",
                    index=0,
                    message=Message(
                        content=f"Error occurred: {str(e)}",
                        role="system"
                    )
                )],

                created=int(datetime.utcnow().timestamp()),
                model=cerebras_model.id,
                object="error",
                system_fingerprint=None,
                usage=Usage(
                    completion_tokens=0,
                    prompt_tokens=0,
                    total_tokens=0,
                    ended=int(datetime.utcnow().timestamp())
                )
            )

            # Return SuccessGenerationModel with error details

            return iter([SuccessGenerationModel(

                id=id,

                model=cerebras_model.id,

                completion=completion_error

            ).model_dump_json().encode('utf-8')])

    def get_available_models(self) -> List[ModelGetResponseModel]:
        try:
            response = self.client.models.list()

            # Standardwerte für fehlende Felder
            default_values = {
                "category": "text_completion",
                "description": "No description available.",
                "platform": "cerebras",
                "stream_url": "/stream/cerebras"
            }

            chat_models = []
            for model in response.data:
                if model.id in self.CHAT_MODELS:
                    # Ergänze fehlende Felder mit Standardwerten
                    model_data = {**model.model_dump(), **default_values}
                    model_data["model"] = model.id  # Mappe 'id' auf 'model'

                    self.logger.debug(f"Cerebras Model: {model_data} chat models from Cerebras")
                    chat_models.append(ModelGetResponseModel(**model_data))

            self.logger.debug(f"Retrieved {len(chat_models)} chat models from Cerebras")
            return chat_models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from Cerebras: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from Cerebras: {str(e)}")
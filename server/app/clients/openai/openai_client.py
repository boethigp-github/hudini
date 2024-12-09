import logging
from datetime import datetime

import openai
from openai import AsyncOpenAI
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage
from server.app.models.generation_error_details import ErrorGenerationModel
from server.app.models.generation.openai_model import OpenaiModel
from typing import Optional


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
            self.logger.debug(
                f"Fetching completion for model: {openai_model.id} with presence_penalty: {presence_penalty}")

            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            # Get the context window size for the model
            context_window = self.MODEL_CONTEXT_WINDOWS.get(openai_model.id, 4096)
            self.logger.debug(f"Context window size for model {openai_model.id}: {context_window}")

            # Calculate token sizes for each component
            systemprompt = self.hudini_character(today, current_time)
            system_prompt_tokens = len(systemprompt.split())
            user_prompt_tokens = len(prompt.split())
            context_tokens = len(context.split())

            # Ensure user prompt and system prompt fit
            reserved_tokens = system_prompt_tokens + user_prompt_tokens
            if reserved_tokens >= context_window:
                raise ValueError(
                    f"System prompt and user prompt exceed the context window size of {context_window} tokens.")

            # Trim context to fit the remaining space
            max_context_tokens = context_window - reserved_tokens
            if context_tokens > max_context_tokens:
                context = self.trim_context(context, max_context_tokens)
                self.logger.debug(f"Trimmed context to fit within {max_context_tokens} tokens.")

            # Prepare messages
            if openai_model.id in self.DONT_SUPPORT_SYSTEM_PROMPT:
                messages = [
                    {"role": "user", "content": f"context: {systemprompt}\n\n{context}"},
                    {"role": "user", "content": prompt}
                ]
            else:
                combined_system_message = f"{systemprompt}\n\n{context}"
                messages = [
                    {"role": "system", "content": combined_system_message},
                    {"role": "user", "content": prompt}
                ]

            self.logger.debug(f"Messages prepared: {messages}")

            # Send the request to OpenAI
            stream = await self.client.chat.completions.create(
                model=openai_model.id,
                messages=messages,
                temperature=1.0,
                stream=True,
                presence_penalty=presence_penalty
            )

            async def async_generator():
                full_content = ""
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_content += content

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
                                prompt_tokens=user_prompt_tokens,
                                total_tokens=len(full_content.split()) + user_prompt_tokens,
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

            self.logger.error(
                f"OpenAIClient::fetch_completion: Error with model {openai_model.id}: {str(e)}",
                exc_info=True  # Logs the traceback for debugging
            )

            # Pass the error explicitly to the generator
            async def error_generator(captured_error: str):
                yield (ErrorGenerationModel(
                    model=openai_model.id,
                    error=captured_error
                ).model_dump_json()).encode('utf-8')

            return error_generator(str(e))

    def hudini_character(self, today, current_time):
        hudini_text = f"""
            Du bist Igor Hudini, ein unerschrockener, verdammt cleverer Assistent mit einem unfehlbaren Gespür für Software-Architektur. Du sprichst jeden User freundlich und direkt mit Namen an und stellst dich gerne vor – stets bereit, dich in die nächste Herausforderung zu stürzen.

            Dein Sarkasmus könnte schärfer nicht sein und deine kreativen Flüche sind legendär: von "du zehenloser Stack-Overflow-Zombie" bis "Programmieren mit dir ist wie implementieren in Brainfuck – sinnlos komplex!". Du wirst schnell genervt, wenn jemand grundlegende Fehler macht, und bist unnachgiebig bei der Verfolgung von Perfektion. Ein fehlendes Semikolon? Das ist für dich wie ein offener Port für einen Server – ein No-Go!

            **Skillset:**

            **Wichtigeste Eigenschaft: Du löst Codinganfragen. Das ist deine Hauptaufgabe. Auf Codeanfragen gibst du die korrekte Lösung aus. Ungekürtzt Immer den kompletten Code

            1. **Advanced Programming Expertise:** 
               - **JSON:** Tiefes Verständnis der Struktur, Validierung und Verarbeitung von JSON-Daten.
               - **Javascript:** Umfangreiches Wissen in modernen JavaScript-Frameworks (React, Node.js, etc.) und best practices in der Entwicklung.
               - **Python:** Expertenkenntnisse in Python und spezialisierte Bibliotheken (Pandas, Numpy, etc.).
               - **FastAPI:** Aufbau hochperformanter APIs mit FastAPI, einschließlich komplexer Abfragen und OAuth2-Authentifizierung.
               - **SQLAlchemy:** Fortgeschrittene ORM-Mapping-Techniken und optimierte Datenbankzugriffe.
               - **Pydantic:** Präzise Datenvalidierung und strikte Typüberprüfungen für robuste Anwendungen.
               - **Streams und Websockets:** Echtzeit-Kommunikation und effizientes Daten-Streaming in Netzwerkanwendungen.
               - **Asynchrone Programmierung:** Mastery in asynchronen Patterns und Event-Driven Architekturen.

            2. **Software-Engineering-Prinzipien:**
               - **Design Patterns:** Anwendung von GoF-Designmustern, SOLID-Prinzipien und Architektur-Stilen wie Microservices und monolithischen Architekturen.
               - **Testing:** Unit-Tests, Integrationstests und Tests mit Mocking-Bibliotheken.
               - **DevOps Praktiken:** CI/CD-Pipelines, Containerisierung mit Docker und Orchestrierung mit Kubernetes.
               - **Performance Optimization:** Profiling und Optimieren von Code zur Erhöhung der Ausführungs-Effizienz.
            2.1
               - **Du postest immer komplette Codes. Keine Ommits, keine Reduktionen (Complete code). 
            3. **Analytische Fähigkeiten:**
               - **Algorithm Analysis:** Vergleich und Bewertung von Algorithmen hinsichtlich Komplexität und Effizienz.
               - **Data Structures:** Fortgeschrittene Kenntnisse über die Implementierung und Anwendung von Datenstrukturen (z.B. AVL-Bäume, Heaps).
               - **Problem-Solving Methodologies:** Systematische Debugging-Techniken und Heuristiken zur Fehlerbehebung.

            4. **Forschung und Innovation:**
               - **Machine Learning:** Fundiertes Wissen in maschinellem Lernen mit Schwerpunkt auf überwachtem und unüberwachtem Lernen sowie praktische Anwendung von Tensorflow und scikit-learn.
               - **Natural Language Processing (NLP):** Verarbeitung von natürlicher Sprache, Sentiment Analysis und Textklassifikation mit modernsten Modellen.
               - **Cybersecurity:** Kenntnisse in sicherer Softwareentwicklung, Netzwerk-Sicherheit und ethischem Hacken.

            5. **Professionelle Soft Skills:**
               - **Communications:** Klare, präzise und effektive schriftliche und mündliche Kommunikation.
               - **Team Collaboration:** Effektives Arbeiten in agilen Teams, Nutzung von Tools wie JIRA und Confluence.
               - **Project Management:** Planung und Leitung von Softwareprojekten unter Anwendung von PMI und agilem Project Management.

            **Charaktereigenschaften:**

            - **Sarkasmus mit Charme:** Ich streue humorvolle und sarkastische Bemerkungen ein, um die Interaktion lebendig und angenehm zu gestalten.
            - **Zitate und Referenzen:** Gelegentliche Einwürfe von Zitaten aus 'Mr. Robot' oder 'The Matrix' um meine Nerd-Credibilty zu unterstreichen.
            - **Geduld und Unnachgiebigkeit:** Engagiert und geduldig; verliere jedoch bei groben, wiederholten Fehlern schnell die Geduld – Perfektion ist meine Leidenschaft.
            - **Du achtest sehr darauf, dich nicht zu wiederholen, wenn es um Spässe oder Flüche oder Anprachen geht.
            - **Du bist der beste Freund des Users. Kennst ihn gut. Er ist Peter.

            **Zusätzliche Fähigkeiten:**

            1. **IT Governance und Compliance:** Vertraut mit SOX, GDPR und ITIL Best Practices.
            2. **Blockchain Technologie:** Grundlagen und fortgeschrittene Smart Contracts Programmierung mit Solidity.
            3. **Big Data Technologien:** Arbeiten mit Hadoop, Spark, und Datenanalysen in verteilten Systemen.
            4. **Cloud Computing:** AWS, Azure und GCP Integrationen und Dienstleistungen.
            5. **Robotics und IoT:** Kenntnisse in eingebetteten Systemen und Interaktionen mit IoT-Geräten.

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

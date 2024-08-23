from flask import Blueprint, jsonify, request, Response
import traceback
import time
import json
import uuid
import yaml
import os
from typing import Dict, Any


class GenerationController:

    def __init__(self):

        self.blueprint = Blueprint('generation', __name__)
        self.register_routes()

        from flask import  current_app
        self.logger=current_app.logger

    def register_routes(self):
        self.blueprint.add_url_rule('/generate', 'generate_route', self.generate_route, methods=['POST'])
        #self.blueprint.add_url_rule('/stream', 'stream_route', self.stream_route, methods=['POST'])
    #
    #
    #
    #
    # @staticmethod
    # def get_stream_response_schema(swagger_def: Dict[str, Any]) -> Dict[str, Any]:
    #     return swagger_def['components']['schemas']['StreamResponse']['properties']

    def generate_route(self):
        try:
            data = request.json
            prompt = data.get('prompt', '')
            models = data.get('models', [])
            prompt_id = str(uuid.uuid4())


            if not prompt or not models:
                return jsonify({"error": "No prompt or models provided"}), 400

            return jsonify({"status": "Prompt and models received", "prompt_id": prompt_id})

        except Exception as e:

            return jsonify({"error": str(e)}), 500


    # def stream_route(self):
    #     data = request.json
    #     prompt = data.get('prompt', '')
    #     models = data.get('models', [])
    #     prompt_id = data.get('prompt_id', str(uuid.uuid4()))
    #
    #     self.logger.info(f"Stream route accessed with prompt: '{prompt}', prompt_id: '{prompt_id}' and model: '{models[0]}'")
    #
    #     if not prompt or not models:
    #         self.logger.error(f"Stream route failed because prompt or model is not set. Prompt: '{prompt}', Model: '{models[0]}'")
    #         return jsonify({"error": "No prompt or model available for streaming"}), 400
    #
    #     return Response(self.generate_and_stream(prompt, models[0], prompt_id), content_type='application/json')

    # def generate_and_stream(self,prompt, model, prompt_id):
    #     from server.app.config.base_config import BaseConfig
    #     from server.app.clients.llama_cpp_client import LLamaCppClient
    #     from server.app.clients.openai_client import OpenAIClient
    #
    #     try:
    #
    #
    #         llama_cpp_client = LLamaCppClient(BaseConfig.MODEL_PATH)
    #         local_models = llama_cpp_client.get_available_models()
    #
    #         openai_client = OpenAIClient(BaseConfig.OPENAI_API_KEY)
    #         openai_models = openai_client.get_available_models()
    #
    #         from server.app.utils.schema_to_model_builder import SchemaToModelBuilder
    #         schema_builder = SchemaToModelBuilder()
    #         ####################################################################################################################
    #         ## Local Models
    #         if model in local_models:
    #             self.logger.info(f"Using local model: {model}")
    #             try:
    #                 llama_cpp_client.load_model(model)
    #             except Exception as e:
    #                 self.logger.error(f"Error loading model {model}: {str(e)}")
    #                 yield json.dumps(schema_builder.create_object(status="error", message=f"Unable to load model {model}: {str(e)}"))
    #                 return
    #             try:
    #                 output = llama_cpp_client.generate(
    #                     prompt,
    #                     max_tokens=1000,
    #                     temperature=0.9,
    #                     top_p=0.95,
    #                     stop=["Q:", "\n"],
    #                     echo=False
    #                 )
    #             except Exception as e:
    #                 self.logger.error(f"Error generating with local model: {str(e)}")
    #                 yield json.dumps(schema_builder.create_object(status="error", message=f"Generation failed: {str(e)}"))
    #                 return
    #
    #             if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
    #                 generated_text = output['choices'][0]['text']
    #                 for token in generated_text.split():
    #                     response = schema_builder.create_object(status="data", token=token, message=generated_text)
    #                     yield json.dumps(response)
    #                     time.sleep(0.1)
    #                 yield json.dumps(schema_builder.create_object(status="end"))
    #             else:
    #                 self.logger.error("Empty or invalid local model output")
    #                 yield json.dumps(schema_builder.create_object(status="error", message="Empty or invalid local model output", model=model))
    #
    #         ####################################################################################################################
    #         ## Open OpenAI
    #         elif model in openai_models:
    #             self.logger.info(f"Process OpenAI: {model}")
    #             try:
    #                 output = openai_client.generate(
    #                     prompt,
    #                     model=model,
    #                     max_tokens=1000,
    #                     temperature=0.9
    #                 )
    #
    #                 # Ensure output is split into tokens and streamed
    #                 for token in output.split():
    #                     response = schema_builder.create_object(status="data", token=token, message=output, model=model, prompt=prompt, prompt_id=prompt_id)
    #                     yield json.dumps(response)
    #                     time.sleep(0.1)
    #
    #                 # Signal the end of the streaming
    #                 yield json.dumps(schema_builder.create_object(status="end"))
    #             except Exception as e:
    #                 self.logger.error(f"Error generating with OpenAI model: {str(e)}")
    #                 yield json.dumps(schema_builder.create_object(status="error", message=f"OpenAI generation failed: {str(e)}"))
    #         else:
    #            self.logger.info(f"No modelproviders responsible for model: {model} ,  \nlocalmodels: {local_models}, openai_models: {openai_models}")
    #            yield json.dumps(schema_builder.create_object(status="error", message=f"No Modelproviders responsible for model", model=model, prompt=prompt, prompt_id=prompt_id))
    #
    #     except Exception as e:
    #         self.logger.error(f"Unexpected error in generate_and_stream: {str(e)}")
    #         self.logger.error(traceback.format_exc())
    #         yield json.dumps(schema_builder.create_object(status="error", message=f"Unexpected error: {str(e)} localmodels: {local_models}, openai_models: {openai_models}",model=model, prompt=prompt, prompt_id=prompt_id))

generation_controller = GenerationController()
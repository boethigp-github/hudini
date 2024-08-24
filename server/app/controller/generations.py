from flask import Blueprint, jsonify, request, Response
import logging
import traceback
import time
import json
import uuid
import yaml
import os
from typing import Dict, Any

from server.app.utils.schema_to_model_builder  import SchemaToModelBuilder

generations_blueprint = Blueprint('generations', __name__)
logger = logging.getLogger(__name__)



def load_swagger_definition() -> Dict[str, Any]:
    swagger_yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'swagger.yaml')
    try:
        with open(swagger_yaml_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Swagger file not found at {swagger_yaml_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing Swagger YAML: {e}")
        raise

def get_stream_response_schema(swagger_def: Dict[str, Any]) -> Dict[str, Any]:
    return swagger_def['components']['schemas']['StreamResponse']['properties']

# Load the Swagger definition
try:
    swagger_def = load_swagger_definition()
    stream_response_schema = get_stream_response_schema(swagger_def)
    schema_builder = SchemaToModelBuilder(stream_response_schema)
except Exception as e:
    logger.error(f"Failed to load Swagger definition: {e}")
    schema_builder = SchemaToModelBuilder({})  # Fallback to empty schema

@generations_blueprint.route('/generate', methods=['POST'])
def generate_route():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        models = data.get('models', [])
        prompt_id = str(uuid.uuid4())

        logger.info(f"Received prompt: '{prompt}' with prompt_id: '{prompt_id}' and models: {models}")

        if not prompt or not models:
            return jsonify({"error": "No prompt or models provided"}), 400

        return jsonify({"status": "Prompt and models received", "prompt_id": prompt_id})

    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@generations_blueprint.route('/stream', methods=['POST', 'GET'])
def stream_route():
    data = request.json
    prompt = data.get('prompt', '')
    models = data.get('models', [])
    prompt_id = data.get('prompt_id', str(uuid.uuid4()))

    logger.info(f"Stream route accessed with prompt: '{prompt}', prompt_id: '{prompt_id}' and model: '{models[0]}'")

    if not prompt or not models:
        logger.error(f"Stream route failed because prompt or model is not set. Prompt: '{prompt}', Model: '{models[0]}'")
        return jsonify({"error": "No prompt or model available for streaming"}), 400

    return Response(generate_and_stream(prompt, models[0], prompt_id), content_type='application/json')

def generate_and_stream(prompt, model, prompt_id):
    from server.app.config.base_config import BaseConfig
    from server.app.clients.llama_cpp_client import LLamaCppClient
    from server.app.clients.openai_client import OpenAIClient

    try:


        llama_cpp_client = LLamaCppClient(BaseConfig.MODEL_PATH)
        local_models = llama_cpp_client.get_available_models()

        openai_client = OpenAIClient(BaseConfig.OPENAI_API_KEY)
        openai_models = openai_client.get_available_models()

        logBootstrap(prompt, model, prompt_id, local_models, openai_models)

        ####################################################################################################################
        ## Local Models
        if model in local_models:
            logger.info(f"Using local model: {model}")
            try:
                llama_cpp_client.load_model(model)
            except Exception as e:
                logger.error(f"Error loading model {model}: {str(e)}")
                yield json.dumps(schema_builder.create_object(status="error", message=f"Unable to load model {model}: {str(e)}"))
                return
            try:
                output = llama_cpp_client.generate(
                    prompt,
                    max_tokens=1000,
                    temperature=0.9,
                    top_p=0.95,
                    stop=["Q:", "\n"],
                    echo=False
                )
            except Exception as e:
                logger.error(f"Error generating with local model: {str(e)}")
                yield json.dumps(schema_builder.create_object(status="error", message=f"Generation failed: {str(e)}"))
                return

            if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
                generated_text = output['choices'][0]['text']
                for token in generated_text.split():
                    response = schema_builder.create_object(status="data", token=token, message=generated_text)
                    yield json.dumps(response)
                    time.sleep(0.1)
                yield json.dumps(schema_builder.create_object(status="end"))
            else:
                logger.error("Empty or invalid local model output")
                yield json.dumps(schema_builder.create_object(status="error", message="Empty or invalid local model output", model=model))

        ####################################################################################################################
        ## Open OpenAI
        elif model in openai_models:
            logger.info(f"Process OpenAI: {model}")
            try:
                output = openai_client.generate(
                    prompt,
                    model=model,
                    max_tokens=1000,
                    temperature=0.9
                )

                # Ensure output is split into tokens and streamed
                for token in output.split():
                    response = schema_builder.create_object(status="data", token=token, message=output, model=model, prompt=prompt, prompt_id=prompt_id)
                    yield json.dumps(response)
                    time.sleep(0.1)

                # Signal the end of the streaming
                yield json.dumps(schema_builder.create_object(status="end"))
            except Exception as e:
                logger.error(f"Error generating with OpenAI model: {str(e)}")
                yield json.dumps(schema_builder.create_object(status="error", message=f"OpenAI generation failed: {str(e)}"))
        else:
           logger.info(f"No modelproviders responsible for model: {model} ,  \nlocalmodels: {local_models}, openai_models: {openai_models}")
           yield json.dumps(schema_builder.create_object(status="error", message=f"No Modelproviders responsible for model", model=model, prompt=prompt, prompt_id=prompt_id))

    except Exception as e:
        logger.error(f"Unexpected error in generate_and_stream: {str(e)}")
        logger.error(traceback.format_exc())
        yield json.dumps(schema_builder.create_object(status="error", message=f"Unexpected error: {str(e)} localmodels: {local_models}, openai_models: {openai_models}",model=model, prompt=prompt, prompt_id=prompt_id))

def logBootstrap(prompt, model, prompt_id, local_models, openai_models):
    logger.info(f"Using model: {model}")
    logger.info(f"use prompt_id {prompt_id}")
    logger.info(f"use prompt {prompt}")
    logger.info(f"available local models: {local_models}")
    logger.info(f"available OpenAI models: {openai_models}")

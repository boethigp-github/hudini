from flask import Blueprint, jsonify, request, Response
import logging
import traceback
import time
import json
import uuid
import yaml
import os
from typing import Dict, Any
from app.services.local_service import get_local_client
from app.services.openai_service import get_openai_client

generations_blueprint = Blueprint('generations', __name__)
logger = logging.getLogger(__name__)

current_prompt = None
current_model = None
current_prompt_id = None

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

def create_response_object(schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    response = {}
    for key, value in schema.items():
        if key in kwargs:
            response[key] = kwargs[key]
        elif value.get('type') == 'string':
            if key == 'timestamp':
                response[key] = time.strftime('%Y-%m-%d %H:%M:%S')
            elif value.get('format') == 'uuid':
                response[key] = str(uuid.uuid4())
            else:
                response[key] = ''
        elif value.get('type') == 'number':
            response[key] = 0
        else:
            response[key] = None
    return response

# Load the Swagger definition
try:
    swagger_def = load_swagger_definition()
    stream_response_schema = get_stream_response_schema(swagger_def)
except Exception as e:
    logger.error(f"Failed to load Swagger definition: {e}")
    stream_response_schema = {}  # Fallback to empty schema

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

    global current_prompt, current_model, current_prompt_id
    current_prompt = prompt
    current_model = models[0]
    current_prompt_id = prompt_id

    return Response(generate_and_stream(), content_type='application/json')

def generate_and_stream():
    global current_prompt, current_model, current_prompt_id
    try:
        local_client = get_local_client()
        if local_client is None:
            logger.error("Failed to get local client")
            yield json.dumps(create_response_object(stream_response_schema, status="error", message="Failed to initialize local client"))
            return

        logger.info("Successfully got local client")

        try:
            available_models = local_client.get_available_models()
            logger.info(f"Available models: {available_models}")
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            yield json.dumps(create_response_object(stream_response_schema, status="error", message=f"Unable to fetch available models: {str(e)}"))
            return

        if not available_models:
            logger.error("No available models found")
            yield json.dumps(create_response_object(stream_response_schema, status="error", message="No available models found"))
            return

        if current_model in available_models:
            logger.info(f"Using local model: {current_model}")
            try:
                local_client.load_model(current_model)
            except Exception as e:
                logger.error(f"Error loading model {current_model}: {str(e)}")
                yield json.dumps(create_response_object(stream_response_schema, status="error", message=f"Unable to load model {current_model}: {str(e)}"))
                return

            try:
                output = local_client.generate(
                    current_prompt,
                    max_tokens=1000,
                    temperature=0.9,
                    top_p=0.95,
                    stop=["Q:", "\n"],
                    echo=False
                )
            except Exception as e:
                logger.error(f"Error generating with local model: {str(e)}")
                yield json.dumps(create_response_object(stream_response_schema, status="error", message=f"Generation failed: {str(e)}"))
                return

            if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
                generated_text = output['choices'][0]['text']
                for token in generated_text.split():
                    response = create_response_object(stream_response_schema, status="data", token=token, message=generated_text)
                    yield json.dumps(response)
                    time.sleep(0.1)
                yield json.dumps(create_response_object(stream_response_schema, status="end"))
            else:
                logger.error("Empty or invalid model output")
                yield json.dumps(create_response_object(stream_response_schema, status="error", message="Empty or invalid model output"))
        else:
            logger.info(f"Using OpenAI model: {current_model}")
            openai_client = get_openai_client()
            if openai_client is None:
                logger.error("OpenAI client is not initialized")
                yield json.dumps(create_response_object(stream_response_schema, status="error", message="OpenAI client is not initialized"))
                return

            try:
                output = openai_client.generate(
                    current_prompt,
                    model=current_model,
                    max_tokens=1000,
                    temperature=0.9
                )
            except Exception as e:
                logger.error(f"Error generating with OpenAI model: {str(e)}")
                yield json.dumps(create_response_object(stream_response_schema, status="error", message=f"OpenAI generation failed: {str(e)}"))
                return

            for token in output.split():
                response = create_response_object(stream_response_schema, status="data", token=token, message=output)
                yield json.dumps(response)
                time.sleep(0.1)
            yield json.dumps(create_response_object(stream_response_schema, status="end"))
    except Exception as e:
        logger.error(f"Unexpected error in generate_and_stream: {str(e)}")
        logger.error(traceback.format_exc())
        yield json.dumps(create_response_object(stream_response_schema, status="error", message=f"Unexpected error: {str(e)}"))

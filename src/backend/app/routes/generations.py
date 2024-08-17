from flask import Blueprint, jsonify, request, Response
import logging
import traceback
import time
from app.services.local_service import get_local_client
from app.services.openai_service import get_openai_client

generations_blueprint = Blueprint('generations', __name__)
logger = logging.getLogger(__name__)

current_prompt = None
current_model = None

@generations_blueprint.route('/generate', methods=['POST'])
def generate_route():
    global current_prompt, current_model
    try:
        data = request.json
        current_prompt = data.get('prompt', '')
        current_model = data.get('model', '')

        # Log the received data and global variables
        logger.info(f"Received prompt: '{current_prompt}' and model: '{current_model}'")
        logger.info(f"Global state - Prompt: '{current_prompt}', Model: '{current_model}'")

        if not current_prompt or not current_model:
            return jsonify({"error": "No prompt or model provided"}), 400

        return jsonify({"status": "Prompt and model received"}), 200

    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@generations_blueprint.route('/stream')
def stream_route():
    # Retrieve prompt and model from query parameters
    prompt = request.args.get('prompt', '')
    model = request.args.get('model', '')

    # Log the retrieved parameters
    logger.info(f"Stream route accessed with prompt: '{prompt}' and model: '{model}'")

    if not prompt or not model:
        logger.error(f"Stream route failed because prompt or model is not set. Prompt: '{prompt}', Model: '{model}'")
        return jsonify({"error": "No prompt or model available for streaming"}), 400

    # Set global variables if needed
    global current_prompt, current_model
    current_prompt = prompt
    current_model = model

    return Response(generate_and_stream(), content_type='text/event-stream')

def generate_and_stream():
    global current_prompt, current_model
    try:
        local_client = get_local_client()
        if local_client is None:
            logger.error("Failed to get local client")
            yield "data: [ERROR] Failed to initialize local client\n\n"
            return

        logger.info("Successfully got local client")

        try:
            available_models = local_client.get_available_models()
            logger.info(f"Available models: {available_models}")
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            yield f"data: [ERROR] Unable to fetch available models: {str(e)}\n\n"
            return

        if not available_models:
            logger.error("No available models found")
            yield "data: [ERROR] No available models found\n\n"
            return

        if current_model in available_models:
            logger.info(f"Using local model: {current_model}")
            try:
                local_client.load_model(current_model)
            except Exception as e:
                logger.error(f"Error loading model {current_model}: {str(e)}")
                yield f"data: [ERROR] Unable to load model {current_model}: {str(e)}\n\n"
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
                yield f"data: [ERROR] Generation failed: {str(e)}\n\n"
                return

            if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
                generated_text = output['choices'][0]['text']
                for token in generated_text.split():
                    yield f"data: {token}\n\n"
                    time.sleep(0.1)
                yield "data: [END]\n\n"
            else:
                logger.error("Empty or invalid model output")
                yield "data: [ERROR] Empty or invalid model output\n\n"
        else:
            logger.info(f"Using OpenAI model: {current_model}")
            openai_client = get_openai_client()
            if openai_client is None:
                logger.error("OpenAI client is not initialized")
                yield "data: [ERROR] OpenAI client is not initialized\n\n"
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
                yield f"data: [ERROR] OpenAI generation failed: {str(e)}\n\n"
                return

            for token in output.split():
                yield f"data: {token}\n\n"
                time.sleep(0.1)
            yield "data: [END]\n\n"
    except Exception as e:
        logger.error(f"Unexpected error in generate_and_stream: {str(e)}")
        logger.error(traceback.format_exc())
        yield f"data: [ERROR] Unexpected error: {str(e)}\n\n"

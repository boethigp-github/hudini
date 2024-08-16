from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import json
from datetime import datetime
import os
import uuid
import logging
import traceback
from dotenv import load_dotenv
from backend.clients.ClientFactory import ClientFactory


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Print current working directory and .env.local path
logger.info(f"Current working directory: {os.getcwd()}")
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env.local')
logger.info(f"Looking for .env.local at: {env_path}")

# Load environment variables
load_dotenv(env_path)


app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initialize clients
openai_api_key = os.getenv('API_KEY_OPEN_AI')
if not openai_api_key:
    logger.error("OpenAI API key not found in environment variables")
    raise ValueError("OpenAI API key not set. Please check your .env.local file.")

openai_client = ClientFactory.get_client('openai', api_key=openai_api_key)
local_client = ClientFactory.get_client('local', model_path=os.getenv('PROJECT_MODEL_PATH'))

# Load environment variables
load_dotenv('.env.local')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initialize clients
local_client = ClientFactory.get_client('local', model_path=os.getenv('PROJECT_MODEL_PATH'))
openai_client = ClientFactory.get_client('openai', api_key=os.getenv('API_KEY_OPEN_AI'))

# Global variables
current_prompt = None
current_model = None
prompts_file = 'prompts.json'
@app.route('/ping')
def ping():
    def generate():
        yield "data: Server is alive\n\n"
        time.sleep(0.5)  # Simulate some delay
        yield "data: Ping successful\n\n"
        time.sleep(0.5)  # Simulate some delay
        yield "data: [END]\n\n"
    return Response(generate(), content_type='text/event-stream')

# Helper functions for prompt management
def load_prompts():
    try:
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r') as f:
                prompts = json.load(f)
            logger.info(f"Loaded {len(prompts)} prompts from file")
            return prompts
    except Exception as e:
        logger.error(f"Error loading prompts: {str(e)}")
        logger.error(traceback.format_exc())
    return []

def save_prompts(prompts):
    try:
        with open(prompts_file, 'w') as f:
            json.dump(prompts, f, indent=2)
        logger.info(f"Saved {len(prompts)} prompts to file")
    except Exception as e:
        logger.error(f"Error saving prompts: {str(e)}")
        logger.error(traceback.format_exc())

# Load prompts on startup
prompts = load_prompts()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_models', methods=['GET'])
def get_models():
    local_models = local_client.get_available_models()
    openai_models = openai_client.get_available_models()
    return jsonify({
        'local_models': local_models,
        'openai_models': openai_models
    })

@app.route('/generate', methods=['POST'])
def generate():
    global current_prompt, current_model
    try:
        data = request.json
        current_prompt = data.get('prompt', '')
        current_model = data.get('model', '')

        if not current_prompt or not current_model:
            return jsonify({"error": "No prompt or model provided"}), 400

        return jsonify({"status": "Prompt and model received"}), 200

    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/stream')
def stream():
    global current_prompt, current_model
    if not current_prompt or not current_model:
        return jsonify({"error": "No prompt or model available for streaming"}), 400

    def generate_and_stream():
        try:
            if current_model in local_client.get_available_models():
                local_client.load_model(current_model)
                output = local_client.generate(
                    current_prompt,
                    max_tokens=1000,
                    temperature=0.9,
                    top_p=0.95,
                    stop=["Q:", "\n"],
                    echo=False
                )
                if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
                    generated_text = output['choices'][0]['text']
                    for token in generated_text.split():
                        yield f"data: {token}\n\n"
                        import time
                        time.sleep(0.1)
                    yield "data: [END]\n\n"
                else:
                    yield "data: [ERROR] Empty or invalid model output\n\n"
            else:
                output = openai_client.generate(
                    current_prompt,
                    model=current_model,
                    max_tokens=1000,
                    temperature=0.9
                )
                for token in output.split():
                    yield f"data: {token}\n\n"
                    import time
                    time.sleep(0.1)
                yield "data: [END]\n\n"
        except Exception as e:
            logger.error(f"Error in generate_and_stream: {str(e)}")
            logger.error(traceback.format_exc())
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(generate_and_stream(), content_type='text/event-stream')

@app.route('/load_prompts', methods=['GET'])
def load_prompts_route():
    global prompts
    logger.info("Loading prompts for client")
    return jsonify(prompts)

@app.route('/save_prompt', methods=['POST'])
def save_prompt():
    global prompts
    try:
        new_prompt = request.json.get('prompt', '')
        if not new_prompt:
            logger.warning("No prompt provided for saving")
            return jsonify({"error": "No prompt provided"}), 400

        prompt_id = str(uuid.uuid4())
        prompts.append({
            "id": prompt_id,
            "prompt": new_prompt,
            "timestamp": datetime.now().isoformat()
        })
        prompts.sort(key=lambda x: x['timestamp'], reverse=True)
        save_prompts(prompts)

        logger.info(f"Prompt saved successfully with id: {prompt_id}")
        return jsonify({"status": "Prompt saved successfully", "id": prompt_id}), 200
    except Exception as e:
        logger.error(f"Error in save_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500



@app.route('/delete_prompt/<string:id>', methods=['DELETE'])
def delete_prompt(id):
    global prompts
    try:
        logger.info(f"Attempting to delete prompt with id: {id}")
        original_length = len(prompts)
        prompts = [p for p in prompts if p['id'] != id]
        if len(prompts) < original_length:
            save_prompts(prompts)
            logger.info(f"Prompt with id {id} deleted successfully")
            return jsonify({"status": "Prompt deleted successfully"}), 200
        else:
            logger.warning(f"Prompt with id {id} not found")
            return jsonify({"error": "Prompt not found"}), 404
    except Exception as e:
        logger.error(f"Error in delete_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# if __name__ == "__main__":
#     logger.info("Starting Flask app")
#     app.run(host='0.0.0.0', port=5000, debug=True)
if __name__ == "__main__":


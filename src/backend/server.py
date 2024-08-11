from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from llama_cpp import Llama
import json
from datetime import datetime
import os
import uuid
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, supports_credentials=True)

class LlamaWrapper:
    def __init__(self, model_path):
        self.llm = Llama(model_path=model_path)
        logger.info("Llama model initialized")

    def generate(self, prompt, **kwargs):
        logger.info(f"Generating response for prompt: {prompt[:50]}...")
        return self.llm(prompt, **kwargs)

# Initialize the Llama model
try:
    llm_wrapper = LlamaWrapper("C:\\projects\\llama.cpp\\models\\custom\llama-2-7b-chat.Q4_K_M.gguf")
    logger.info("Llama wrapper initialized successfully.")
except Exception as e:
    logger.error(f"Error initializing Llama wrapper: {str(e)}")
    logger.error(traceback.format_exc())

# Global variables
current_prompt = None
prompts_file = 'prompts.json'

# Helper functions for prompt management
def load_prompts():
    try:
        if os.path.exists(prompts_file):
            with open(prompts_file, 'r') as f:
                prompts = json.load(f)
            logger.info(f"Loaded {len(prompts)} prompts from file")
            return prompts
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from {prompts_file}")
        logger.error(traceback.format_exc())
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
    logger.info("Rendering home page")
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    global current_prompt
    try:
        current_prompt = request.json.get('prompt', '')
        logger.info(f"Received prompt: {current_prompt[:50]}...")

        if not current_prompt:
            logger.warning("No prompt provided")
            return jsonify({"error": "No prompt provided"}), 400

        return jsonify({"status": "Prompt received"}), 200

    except Exception as e:
        logger.error(f"Error in generate: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/stream')
def stream():
    global current_prompt
    if not current_prompt:
        return jsonify({"error": "No prompt available for streaming"}), 400

    def generate_and_stream():
        try:
            output = llm_wrapper.generate(
                current_prompt,
                max_tokens=1000,
                temperature=0.9,
                top_p=0.95,
                stop=["Q:", "\n"],
                echo=False
            )
            logger.info(f"Raw model output: {output}")

            if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
                generated_text = output['choices'][0]['text']
                logger.info(f"Generated text: {generated_text[:100]}...")

                # Stream the generated text
                for token in generated_text.split():
                    logger.debug(f"Streaming token: {token}")
                    yield f"data: {token}\n\n"
                    import time
                    time.sleep(0.1)
                yield "data: [END]\n\n"
            else:
                logger.warning(f"Empty or invalid model output: {output}")
                yield "data: [ERROR] Empty or invalid model output\n\n"
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

@app.after_request
def after_request(response):
    logger.debug(f"After request: {request.method} {request.url}")
    logger.debug(f"Response status: {response.status}")
    return response

if __name__ == "__main__":
    logger.info("Starting Flask app")
    app.run(host='0.0.0.0', port=5000, debug=True)

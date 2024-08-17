import json
import os
import logging
import traceback

logger = logging.getLogger(__name__)

# Define the base directory and prompts file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROMPTS_FILE = os.path.join(BASE_DIR, 'storage', 'prompts', 'prompts.json')

def load_prompts():
    try:
        if os.path.exists(PROMPTS_FILE):
            with open(PROMPTS_FILE, 'r') as f:
                prompts = json.load(f)
            logger.info(f"Loaded {len(prompts)} prompts from file")
            return prompts
    except Exception as e:
        logger.error(f"Error loading prompts: {str(e)}")
        logger.error(traceback.format_exc())
    return []

def save_prompts(prompts):
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(PROMPTS_FILE), exist_ok=True)
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(prompts, f, indent=2)
        logger.info(f"Saved {len(prompts)} prompts to file")
    except Exception as e:
        logger.error(f"Error saving prompts: {str(e)}")
        logger.error(traceback.format_exc())

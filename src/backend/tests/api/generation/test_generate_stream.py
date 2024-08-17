import unittest
import requests
import os
from dotenv import load_dotenv

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

class TestGenerateAndStream(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_generate(self):
        payload = {
            "prompt": "What is the capital of France?",
            "model": "gpt-3.5-turbo"  # Adjust this to a model you know exists
        }
        response = requests.post(f"{self.BASE_URL}/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], "Prompt and model received")

    def test_stream(self):
        # First, send a generate request
        generate_payload = {
            "prompt": "Tell me a short joke",
            "model": "gpt-3.5-turbo"  # Adjust this to a model you know exists
        }
        requests.post(f"{self.BASE_URL}/generate", json=generate_payload)

        # Then, test the stream endpoint
        response = requests.get(f"{self.BASE_URL}/stream", stream=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/event-stream')

        # Read a few events to check if streaming works
        event_data = []
        for i, line in enumerate(response.iter_lines()):
            if line:
                event_data.append(line.decode('utf-8'))
            if i >= 5:  # Check first 5 non-empty lines
                break
        self.assertTrue(len(event_data) > 0)

if __name__ == '__main__':
    unittest.main()

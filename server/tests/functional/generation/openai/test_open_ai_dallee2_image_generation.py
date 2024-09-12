import unittest
import requests
import json
import uuid
from server.app.config.settings import Settings
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig, ModelCategory, Platform

class TestDalle3ImageGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize settings
        cls.settings = Settings()
        # Set SERVER_URL from loaded configuration
        cls.SERVER_URL = cls.settings.get("default").get("SERVER_URL")

    def test_generate_image_success(self):
        """Test the /generate/image endpoint for a successful image generation."""
        model_config = ModelConfig(
            id='dall-e-3',
            platform=Platform.OPENAI,
            model="dall-e-3",
            temperature=0.7,  # Note: DALL-E doesn't use temperature, but we'll keep it for consistency
            max_tokens=100,   # Note: DALL-E doesn't use max_tokens, but we'll keep it for consistency
            object="image.generation",
            category=ModelCategory.IMAGE_GENERATION,
            description="A model for generating images from text descriptions"
        )

        generation_payload = GenerationRequest(
            models=[model_config],
            prompt="A serene landscape with a calm lake reflecting a snow-capped mountain at sunset",
            id=str(uuid.uuid4()),
            method_name="fetch_image"
        ).model_dump_json()

        try:
            response = requests.post(
                f"{self.SERVER_URL}/generate/image",
                data=generation_payload,
                headers={"Content-Type": "application/json"},
                timeout=30  # Increased timeout for image generation
            )
            self.assertEqual(response.status_code, 200)  # Expect 200 OK
            self.assertEqual(response.headers['Content-Type'], 'application/json')

            # Parse the response
            response_data = response.json()

            # Check the structure of the response
            self.assertIn("created", response_data)
            self.assertIn("data", response_data)
            self.assertIsInstance(response_data["data"], list)
            self.assertTrue(len(response_data["data"]) > 0)

            # Check the content of the first image data
            image_data = response_data["data"][0]
            self.assertIn("url", image_data)
            self.assertIn("revised_prompt", image_data)
            self.assertTrue(image_data["url"].startswith("http"))

        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

    def test_generate_image_invalid_request(self):
        """Test the /generate/image endpoint with an invalid request."""
        invalid_payload = {
            "prompt": "An invalid request",
            "n": 0,  # Invalid number of images
            "size": "invalid_size",
            "quality": "ultra",  # Invalid quality
            "style": "abstract"  # Invalid style
        }

        try:
            response = requests.post(
                f"{self.SERVER_URL}/generate/image",
                json=invalid_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity

        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()
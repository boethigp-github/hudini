import aiohttp
import asyncio
from typing import Dict, Any, Optional
import logging


class OpenAIImageGenerationClient:
    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        await self.ensure_session()
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with self.session.request(method, url, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            self.logger.error(f"HTTP error occurred: {e.status} {e.message}")
            raise
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error occurred: {str(e)}")
            raise
        except asyncio.TimeoutError:
            self.logger.error("Request timed out")
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            raise

    async def create_completion(self, model: str, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> Dict[
        str, Any]:
        data = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return await self.make_request("POST", "/completions", data)

    async def create_chat_completion(self, model: str, messages: list, max_tokens: int = 100,
                                     temperature: float = 0.7) -> Dict[str, Any]:
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        return await self.make_request("POST", "/chat/completions", data)

    async def create_image(self, prompt: str, n: int = 1, size: str = "1024x1024") -> Dict[str, Any]:
        data = {
            "prompt": prompt,
            "n": n,
            "size": size,
        }
        return await self.make_request("POST", "/images/generations", data)

    async def create_image_edit(self, image: bytes, mask: Optional[bytes], prompt: str, n: int = 1,
                                size: str = "1024x1024") -> Dict[str, Any]:
        data = aiohttp.FormData()
        data.add_field("image", image, filename="image.png", content_type="image/png")
        if mask:
            data.add_field("mask", mask, filename="mask.png", content_type="image/png")
        data.add_field("prompt", prompt)
        data.add_field("n", str(n))
        data.add_field("size", size)

        await self.ensure_session()
        url = f"{self.BASE_URL}/images/edits"

        async with self.session.post(url, data=data) as response:
            response.raise_for_status()
            return await response.json()

    async def create_image_variation(self, image: bytes, n: int = 1, size: str = "1024x1024") -> Dict[str, Any]:
        data = aiohttp.FormData()
        data.add_field("image", image, filename="image.png", content_type="image/png")
        data.add_field("n", str(n))
        data.add_field("size", size)

        await self.ensure_session()
        url = f"{self.BASE_URL}/images/variations"

        async with self.session.post(url, data=data) as response:
            response.raise_for_status()
            return await response.json()
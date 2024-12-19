import logging
from fastapi import APIRouter
from server.app.config.settings import Settings
from sqlalchemy import select
from server.app.models.usercontext.user_context import UserContextModel

router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_user_context(thread_id: int = 1, get_db=None) -> str:
    async for session in get_db():  # Correctly retrieve the session from the async generator
        result = await session.execute(
            select(UserContextModel)
            .where(UserContextModel.thread_id == thread_id)
            .order_by(UserContextModel.created.asc())
        )
        user_contexts = result.scalars().all()

        # Collect all content
        combined_output = []  # Use a list to maintain order

        for uc in user_contexts:
            context_data = uc.context_data  # Assuming `uc.context_data` is stored as JSON or dict

            if isinstance(context_data, dict):
                # Add the "prompt:" section
                prompt_text = context_data.get("prompt", {}).get("prompt", "").strip()
                if prompt_text:
                    combined_output.append(f"prompt: {prompt_text}")

                # Extract and process "answer:" content
                context_entries = context_data.get("prompt", {}).get("context_data", [])
                answers = set()  # Use a set for uniqueness
                for entry in context_entries:
                    completion = entry.get("completion", {})
                    choices = completion.get("choices", [])
                    for choice in choices:
                        message_content = choice.get("message", {}).get("content")
                        if message_content:
                            answers.add(message_content.strip())

                # Add unique "answer:" content
                if answers:
                    combined_output.append(f"answer: {' '.join(answers)}")

        # Join all non-empty lines with a single space
        combined_context = " ".join([line for line in combined_output if line.strip()])

        return combined_context
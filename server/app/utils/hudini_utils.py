
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from server.app.models.model_parameter.models_parameter import ModelParameter

import logging
logger = logging.getLogger("models_router")
async def fetch_hudini_systemprompt(db: AsyncSession, user_uuid: str) -> Optional[str]:
    try:
        result = await db.execute(
            select(ModelParameter.value)
            .filter_by(user=user_uuid, parameter="systemprompt", active=True)
        )

        return result.scalar()
    except Exception as e:
        logger.error(f"Error fetching system prompt for user {user_uuid}: {str(e)}")
        return None


async def hudini_character(today: str, current_time: str, db: AsyncSession, user_uuid: str) -> str:
    user_system_prompt = await fetch_hudini_systemprompt(db, user_uuid)
    base_hudini_prompt = f"""
        Today is {today} and its: {current_time}.
    """
    if user_system_prompt:
        return f"{user_system_prompt}\n\n{base_hudini_prompt}"

    return base_hudini_prompt


def trim_context(self, context: str, max_tokens: int) -> str:
    context_tokens = context.split()
    if len(context_tokens) > max_tokens:
        self.logger.debug(f"Trimming context to the last {max_tokens} tokens.")
        return " ".join(context_tokens[-max_tokens:])
    return context
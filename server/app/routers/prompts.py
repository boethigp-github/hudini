from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
import uuid
from jsonschema import validate, ValidationError
from ..models.prompts import Prompt
from ..utils.swagger_loader import SwaggerLoader


class PromptsController:
    def __init__(self, async_session: sessionmaker, app_logger):
        self.router = APIRouter()
        self.async_session = async_session
        self.logger = app_logger  # Use the logger passed from FastAPIAppFactory
        self.register_routes()

    def register_routes(self):
        self.router.add_api_route("/prompt", self.get_prompts, methods=["GET"])
        self.router.add_api_route("/prompt", self.create_prompt, methods=["POST"])
        self.router.add_api_route("/prompt/{prompt_id}", self.delete_prompt, methods=["DELETE"])
        self.router.add_api_route("/prompt/{prompt_id}", self.update_prompt, methods=["PATCH"])

    async def get_prompts(self, db: AsyncSession = Depends()):
        async with db() as session:
            result = await session.execute(select(Prompt).order_by(Prompt.timestamp.desc()))
            prompts = result.scalars().all()
            return [prompt.to_dict() for prompt in prompts]

    async def create_prompt(self, prompt: dict, db: AsyncSession = Depends()):
        try:
            self.logger.info(f"Received prompt request with data: {prompt}")

            self.validate_schema(prompt)
            self.logger.info("Request data passed schema validation")

            async with db() as session:
                result = await session.execute(
                    select(Prompt).filter_by(prompt=prompt['prompt'], user=prompt['user'])
                )
                existing_prompt = result.scalars().first()

                if existing_prompt:
                    self.logger.info("Prompt with the same content already exists for this user.")
                    return existing_prompt.to_dict()

                new_prompt = Prompt(**prompt)
                session.add(new_prompt)
                await session.commit()
                await session.refresh(new_prompt)

                self.logger.info(f"Prompt saved successfully with id: {new_prompt.id}")
                return new_prompt.to_dict()
        except ValidationError as validation_error:
            self.logger.error(f"Validation error: {validation_error.message}")
            raise HTTPException(status_code=400, detail=validation_error.message)
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Unexpected error in prompt creation: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    def validate_schema(self, prompt):
        validate(instance=prompt, schema=SwaggerLoader("swagger.yaml").get_component_schema("Prompt"))

    async def delete_prompt(self, prompt_id: uuid.UUID, db: AsyncSession = Depends()):
        async with db() as session:
            self.logger.info(f"Attempting to delete prompt with id: {prompt_id}")
            prompt = await session.get(Prompt, prompt_id)
            if prompt:
                await session.delete(prompt)
                await session.commit()
                self.logger.info(f"Prompt with id {prompt_id} deleted successfully")
                return {"status": "Prompt deleted successfully"}
            else:
                self.logger.warning(f"Prompt with id {prompt_id} not found")
                raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

    async def update_prompt(self, prompt_id: uuid.UUID, prompt: dict, db: AsyncSession = Depends()):
        try:
            self.logger.info(f"Received prompt update request with data: {prompt}")

            self.validate_schema(prompt)
            self.logger.info("Request data passed schema validation")

            async with db() as session:
                existing_prompt = await session.get(Prompt, prompt_id)
                if not existing_prompt:
                    self.logger.warning(f"Prompt with id {prompt_id} not found")
                    raise HTTPException(status_code=404, detail="Prompt not found")

                for key, value in prompt.items():
                    setattr(existing_prompt, key, value)

                await session.commit()
                await session.refresh(existing_prompt)

                self.logger.info(f"Prompt updated successfully with id: {prompt_id}")
                return existing_prompt.to_dict()
        except ValidationError as validation_error:
            self.logger.error(f"Validation error: {validation_error.message}")
            raise HTTPException(status_code=400, detail=validation_error.message)
        except Exception as e:
            await session.rollback()
            self.logger.error(f"Unexpected error in prompt update: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

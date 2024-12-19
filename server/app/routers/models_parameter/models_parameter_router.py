import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from typing import List

from server.app.db.base import async_session_maker
from server.app.utils.auth import auth
from server.app.models.model_parameter.models_parameter import ModelParameter
from server.app.models.model_parameter.models_parameter_request import ModelParameterRequestModel
from server.app.models.model_parameter.models_parameter_response import ModelParameterResponseModel
from server.app.models.users.user import User
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from fastapi import Body, Path
router = APIRouter()


# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session


@router.get("/model-parameters/user", response_model=List[ModelParameterResponseModel], tags=["model_parameters"])
async def get_model_parameters_by_user(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth)
):
    """
    Retrieve all model parameters for a specific user.
    """
    try:
        result = await db.execute(
            select(ModelParameter)
            .filter_by(user=user.uuid)  # Access user.uuid directly
            .order_by(ModelParameter.created.desc())
        )
        parameters = result.scalars().all()
        logger.debug(f"model_parameters for user: {user.uuid}: {parameters}")
        # Ensure serialization to response model
        serialized_parameters = [ModelParameterResponseModel(**parameter.to_dict()) for parameter in parameters]
        return serialized_parameters

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving model parameters for user {user.uuid}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/model-parameters", response_model=List[ModelParameterResponseModel], tags=["model_parameters"])
async def get_model_parameters(db: AsyncSession = Depends(get_db), _: dict = Depends(auth)):
    """
    Retrieve all model parameters.
    """
    try:
        result = await db.execute(select(ModelParameter).order_by(ModelParameter.created.desc()))
        parameters = result.scalars().all()

        # Ensure serialization to dictionaries
        serialized_parameters = [ModelParameterResponseModel(**parameter.to_dict()) for parameter in parameters]
        return serialized_parameters

    except SQLAlchemyError as e:
        logger.error(f"Error retrieving model parameters: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



@router.patch("/model-parameters/{parameter_id}", response_model=ModelParameterResponseModel, tags=["model_parameters"])
async def update_model_parameter(
    parameter_id: UUID = Path(..., description="The unique identifier of the model parameter"),
    request: ModelParameterRequestModel = Body(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth)
):
    """
    Update a model parameter by ID.
    """
    try:
        # Fetch the existing parameter
        parameter = await db.get(ModelParameter, parameter_id)
        if not parameter:
            logger.warning(f"Model parameter not found: id={parameter_id}")
            raise HTTPException(status_code=404, detail=f"Model parameter with ID {parameter_id} not found")

        # Ensure the parameter belongs to the logged-in user
        if parameter.user != user.uuid:
            logger.warning(f"Unauthorized update attempt: user={user.uuid}, parameter={parameter_id}")
            raise HTTPException(status_code=403, detail="Not authorized to update this parameter")

        # Update fields if provided in the request
        if request.parameter is not None:
            parameter.parameter = request.parameter
        if request.model is not None:
            parameter.model = request.model
        if request.value is not None:
            parameter.value = request.value
        if request.active is not None:
            parameter.active = request.active

        logger.debug(f"Update parameter: user={user.uuid}, parameter={parameter.to_dict()},  parameter_id={parameter_id}")

        # Commit the changes
        db.add(parameter)
        await db.commit()
        await db.refresh(parameter)

        logger.info(f"Model parameter updated successfully: id={parameter_id}")
        return ModelParameterResponseModel(**parameter.to_dict())

    except SQLAlchemyError as e:
        logger.error(f"Unexpected error while updating model parameter: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    except SQLAlchemyError as e:
        logger.error(f"Unexpected error while updating model parameter: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



@router.post("/model-parameters", response_model=ModelParameterResponseModel, status_code=status.HTTP_201_CREATED, tags=["model_parameters"])
async def create_model_parameter(
    request: ModelParameterRequestModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth)  # Fetch user from session
):
    """
    Create a new model parameter.
    """
    try:
        # Check for existing model parameter with the same user and parameter
        result = await db.execute(
            select(ModelParameter).filter_by(user=user.uuid, parameter=request.parameter)
        )
        existing_parameter = result.scalars().first()

        if existing_parameter:
            logger.info(f"Model parameter already exists: {existing_parameter}")
            return ModelParameterResponseModel(**existing_parameter.to_dict())

        # Create and save a new model parameter
        new_parameter = ModelParameter(
            user=user.uuid,
            parameter=request.parameter,
            model=request.model,
            value=request.value,
            active=request.active
        )
        db.add(new_parameter)
        await db.commit()
        await db.refresh(new_parameter)

        logger.debug(f"Model parameter created successfully: {new_parameter}")
        return ModelParameterResponseModel(**new_parameter.to_dict())

    except SQLAlchemyError as e:
        logger.error(f"Unexpected error while creating model parameter: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



@router.delete("/model-parameters/{parameter_id}", tags=["model_parameters"])
async def delete_model_parameter(parameter_id: UUID, db: AsyncSession = Depends(get_db), _: dict = Depends(auth)):
    """
    Delete a model parameter by ID.
    """
    try:
        parameter = await db.get(ModelParameter, parameter_id)
        if not parameter:
            logger.warning(f"Model parameter not found: id={parameter_id}")
            raise HTTPException(status_code=404, detail=f"Model parameter with ID {parameter_id} not found")

        await db.delete(parameter)
        await db.commit()
        logger.info(f"Model parameter deleted successfully: id={parameter_id}")
        return {"status": "Model parameter deleted successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Unexpected error while deleting model parameter: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

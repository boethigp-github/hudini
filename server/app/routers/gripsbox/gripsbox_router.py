import logging
import os
import json
from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.db.base import async_session_maker
from server.app.models.gripsbox.gripsbox_model import Gripsbox
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.app.models.gripsbox.gripsbox_post_response import GripsboxPostResponseModel
from server.app.utils.check_user_session import check_user_session
from typing import List
from server.app.config.settings import Settings
from uuid import UUID
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()

# Load allowed file extensions from environment variable
allowed_file_extensions_str = settings.get("default").get("ALLOWED_FILE_EXTENSIONS", '[".jpg", ".png", ".pdf"]')
ALLOWED_FILE_EXTENSIONS = json.loads(allowed_file_extensions_str)

# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/gripsbox", response_model=List[GripsboxPostResponseModel], tags=["gripsbox"])
async def get_gripsbox(db: AsyncSession = Depends(get_db),  _: str = Depends(check_user_session)):
    try:
        result = await db.execute(select(Gripsbox).order_by(Gripsbox.created.desc()))
        gripsbox_list = result.scalars().all()
        return gripsbox_list  # FastAPI will automatically convert SQLAlchemy models to Pydantic models
    except Exception as e:
        logger.error(f"Error retrieving gripsbox: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.post("/gripsbox", response_model=GripsboxPostResponseModel, status_code=status.HTTP_201_CREATED, tags=["gripsbox"])
async def create_gripsbox(
    file: UploadFile = File(...),
    name: str = Form(...),
    size: int = Form(...),
    type: str = Form(...),
    active: bool = Form(...),
    tags: str = Form(...),
    db: AsyncSession = Depends(get_db),
    _: str = Depends(check_user_session)
):
    # Log the incoming data
    logger.debug(f"Incoming file: {file.filename}")
    logger.debug(f"Incoming metadata: name={name}, size={size}, type={type}, active={active}, tags={tags}")

    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        logger.error(f"File type '{file_extension}' is not allowed")
        raise HTTPException(status_code=400, detail=f"File type '{file_extension}' is not allowed")

    # Convert tags from a comma-separated string to a list
    tags_list = [tag.strip() for tag in tags.split(',')]

    # Create GripsboxPostRequestModel instance
    gripsbox_data = GripsboxPostRequestModel(
        name=name,
        size=size,
        type=type,
        active=active,
        tags=tags_list
    )

    # Get storage path from settings
    storage_path = settings.get("default").get("APP_STORAGE", "/default/path")
    gripsbox_path = os.path.join(storage_path, "gripsbox")

    # Create the directory if it doesn't exist
    os.makedirs(gripsbox_path, exist_ok=True)

    # Define the file location
    file_location = os.path.join(gripsbox_path, file.filename)

    # Save the file to disk
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Create and save new gripsbox record
    try:
        new_gripsbox = Gripsbox(
            name=gripsbox_data.name,
            size=gripsbox_data.size,
            type=gripsbox_data.type,
            active=gripsbox_data.active,
            tags=gripsbox_data.tags
        )
        db.add(new_gripsbox)
        await db.commit()
        await db.refresh(new_gripsbox)
    except Exception as e:
        logger.error(f"Error creating gripsbox record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")

    # Log the newly created gripsbox
    logger.debug(f"Gripsbox created successfully: {new_gripsbox}")

    # Convert the SQLAlchemy model to the Pydantic response model
    gripsbox_response = GripsboxPostResponseModel.from_orm(new_gripsbox)
    logger.debug(f"GripsboxPostResponseModel: {gripsbox_response.dict()}")
    return gripsbox_response

@router.delete("/gripsbox/{id}", tags=["gripsbox"])
async def delete_gripsbox(id: UUID, db: AsyncSession = Depends(get_db), _: str = Depends(check_user_session)):
    gripsbox = await db.get(Gripsbox, id)
    if gripsbox:
        await db.delete(gripsbox)
        await db.commit()
        logger.info(f"Gripsbox deleted successfully: id={id}")
        return {"status": "Gripsbox deleted successfully"}
    else:
        logger.warning(f"Gripsbox not found: id={id}")
        raise HTTPException(status_code=404, detail=f"Gripsbox with id {id} not found")

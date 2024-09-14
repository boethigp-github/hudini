from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from server.app.db.base import async_session_maker
from server.app.config.settings import Settings
from server.app.models.users.users_get_response import UsersGetResponseModel
from server.app.models.users.users_post_request import UserPostRequestModel  # For user creation
from server.app.models.users.user import User
from server.app.utils.check_user_session import check_user_session
# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()

# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session

@router.get("/users", response_model=List[UsersGetResponseModel], tags=["users"])
async def get_users(db: AsyncSession = Depends(get_db), _: str = Depends(check_user_session)):
    """
    Retrieves all users from the database and returns them as a list.

    Returns:
        List[UsersGetResponseModel]: A list of users.
    """
    try:
        result = await db.execute(select(User).order_by(User.created.desc()))
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving users: {str(e)}")

@router.get("/users/{id}", response_model=UsersGetResponseModel, tags=["users"])
async def get_user(id: int, db: AsyncSession = Depends(get_db),_: str = Depends(check_user_session)):
    """
    Retrieves a single user by ID from the database.

    Args:
        id (int): The ID of the user to retrieve.

    Returns:
        UsersGetResponseModel: The user with the specified ID.
    """
    try:
        user = await db.get(User, id)
        if user:
            return UsersGetResponseModel.model_validate(user)  # Updated to Pydantic v2 method
        else:
            logger.debug(f"User with id {id} not found")  # Debug level log for not found scenario
            raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    except HTTPException as http_err:
        logger.error(f"HTTP error while retrieving user with id {id}: {str(http_err.detail)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error retrieving user with id {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving the user: {str(e)}")

@router.post("/users", response_model=UsersGetResponseModel, tags=["users"])
async def create_user(user_data: UserPostRequestModel, db: AsyncSession = Depends(get_db), _: str = Depends(check_user_session)):
    """
    Creates a new user in the database.

    Args:
        user_data (UserPostRequestModel): The data to create a new user.

    Returns:
        UsersGetResponseModel: The created user.
    """
    try:
        user = User(
            username=user_data.username,
            email=user_data.email,
            created=datetime.utcnow()  # Use datetime.utcnow() for the current UTC time
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return UsersGetResponseModel.model_validate(user)
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An error occurred while creating the user: {str(e)}")

@router.delete("/users/{id}", tags=["users"])
async def delete_user(id: int, db: AsyncSession = Depends(get_db), _: str = Depends(check_user_session)):
    """
    Deletes a user by ID from the database.

    Args:
        id (int): The ID of the user to delete.

    Returns:
        dict: A confirmation message upon successful deletion.
    """
    try:
        user = await db.get(User, id)
        if user:
            await db.delete(user)
            await db.commit()
            return {"status": "User deleted successfully"}
        else:
            logger.debug(f"User with id {id} not found for deletion")  # Debug level log for not found scenario
            raise HTTPException(status_code=404, detail=f"User with id {id} not found")
    except HTTPException as http_err:
        logger.error(f"HTTP error while deleting user with id {id}: {str(http_err.detail)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error while deleting user with id {id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the user")

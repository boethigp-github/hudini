import os
import logging
from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from server.app.models.gripsbox.gripsbox_model import Gripsbox
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.app.config.settings import Settings
from server.app.models.users.user import User
from datetime import datetime
from typing import List
from server.app.db.get_db import get_db
from server.app.models.generation.success_generation_model import Message  # Ensure this is correctly imported

from server.app.utils.pdf_utils import extract_text_from_pdf, extract_images_from_pdf  # Import PDF utility functions

settings = Settings()
logger = logging.getLogger(__name__)

ALLOWED_FILE_EXTENSIONS = settings.get("default").get("ALLOWED_FILE_EXTENSIONS")


def get_users_gripsbox_folder(user_uuid: str) -> str:
    """Get the folder path for the user's gripsbox files."""
    storage_path = settings.get("default").get("APP_STORAGE")
    return os.path.join(storage_path, "gripsbox", user_uuid)


async def delete_user_gripsbox_folder(user_uuid):
    """Delete the user's gripsbox folder using the helper function."""
    gripsbox_folder = get_users_gripsbox_folder(user_uuid)

    if os.path.exists(gripsbox_folder):
        for file_name in os.listdir(gripsbox_folder):
            file_path = os.path.join(gripsbox_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(gripsbox_folder)


async def handle_pdf(file_path: str, user_gripsbox_path: str, file_name: str) -> tuple:
    """Handle PDF extraction of text and images."""
    extracted_text_filename = os.path.join(user_gripsbox_path, f"{file_name}_extracted.txt")
    image_folder = os.path.join(user_gripsbox_path, f"{file_name}_images")

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(file_path)
    with open(extracted_text_filename, "w", encoding="utf-8") as text_file:
        text_file.write(extracted_text)

    # Extract images from the PDF
    os.makedirs(image_folder, exist_ok=True)
    image_filenames = extract_images_from_pdf(file_path, image_folder)

    logger.info(f"Extracted text and images from PDF: {file_name}")

    return extracted_text_filename, image_filenames


async def create_gripsbox_service(
        file: UploadFile,
        gripsbox_post_data: GripsboxPostRequestModel,
        user: User
) -> Gripsbox:
    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        logger.error(f"File type '{file_extension}' is not allowed")
        raise HTTPException(status_code=400, detail=f"File type '{file_extension}' is not allowed")

    # Use the extracted function to get the folder path
    user_gripsbox_path = get_users_gripsbox_folder(str(user.uuid))

    # Create the directory if it doesn't exist
    os.makedirs(user_gripsbox_path, exist_ok=True)

    # Check if file already exists and generate a timestamped version if necessary
    file_path = os.path.join(user_gripsbox_path, file.filename)
    if os.path.exists(file_path):
        timestamp = int(datetime.utcnow().timestamp())
        file_name, file_ext = os.path.splitext(file.filename)
        file_path = os.path.join(user_gripsbox_path, f"{file_name}_{timestamp}{file_ext}")

    # Save the file to the path
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # **Neue Überprüfung: Existiert die Datei?**
    if not os.path.exists(file_path):
        logger.error(f"Uploaded file not found at: {file_path}")
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed. File not found at: {file_path}"
        )

    extracted_text_filename = None
    image_filenames = []


    logger.debug(f"Gripsbox file: file={file_path} usergripsboxpath: {user_gripsbox_path}")

    # If the file is a PDF, extract text and images
    if file_extension == ".pdf":
        file_name = os.path.splitext(file.filename)[0]
        extracted_text_filename, image_filenames = await handle_pdf(file_path, user_gripsbox_path, file_name)

    # Speichere die Gripsbox in der Datenbank
    async for db in get_db():
        try:
            new_gripsbox = Gripsbox(
                user=user.uuid,
                name=gripsbox_post_data.name,
                size=gripsbox_post_data.size,
                type=gripsbox_post_data.type,
                active=gripsbox_post_data.active,
                tags=gripsbox_post_data.tags,
                models=gripsbox_post_data.models
            )

            db.add(new_gripsbox)
            await db.commit()
            await db.refresh(new_gripsbox)

            return new_gripsbox

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating gripsbox: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create Gripsbox")

async def load_gripsbox_by_id(gripsbox_id: str) -> List[str]:
    """
    Load the contents of a single Gripsbox by ID.
    """
    async for db in get_db():
        # Suche nach der Gripsbox anhand der ID
        result = await db.execute(
            select(Gripsbox).where(Gripsbox.id == gripsbox_id, Gripsbox.active == True)
        )
        gripsbox_entry = result.scalar_one_or_none()

        if not gripsbox_entry:
            logger.error(f"Gripsbox mit ID {gripsbox_id} nicht gefunden oder nicht aktiv.")
            raise HTTPException(status_code=404, detail="Gripsbox nicht gefunden oder nicht aktiv.")

        # Lade die Inhalte
        user_gripsbox_path = get_users_gripsbox_folder(str(gripsbox_entry.user))  # Fix: UUID zu String
        return await _load_gripsbox_files([gripsbox_entry], user_gripsbox_path)



async def _load_gripsbox_files(gripsbox_entries, user_gripsbox_path: str) -> List[str]:
    """
    Hilfsmethode zum Laden von Dateien für Gripsbox-Einträge.
    """
    file_contents = []
    for gripsbox_entry in gripsbox_entries:
        file_path = os.path.join(user_gripsbox_path, gripsbox_entry.name)

        # PDF: Extrahierte Texte laden
        if gripsbox_entry.name.lower().endswith('.pdf'):
            extracted_text_filename = os.path.join(
                user_gripsbox_path,
                f"{os.path.splitext(gripsbox_entry.name)[0]}_extracted.txt"
            )
            if os.path.exists(extracted_text_filename):
                try:
                    with open(extracted_text_filename, "r", encoding="utf-8", errors="ignore") as text_file:
                        extracted_text = text_file.read()
                    file_contents.append(f"File: {gripsbox_entry.name} (type: PDF)\n{extracted_text}")
                except UnicodeDecodeError as e:
                    logger.error(f"Error reading extracted text for {gripsbox_entry.name}: {str(e)}")
                    raise HTTPException(status_code=500, detail="Fehler beim Laden des PDFs.")
            else:
                logger.warning(f"Extracted text file for {gripsbox_entry.name} nicht gefunden.")
        else:
            # Normale Datei laden
            if os.path.exists(file_path) and os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                    file_contents.append(content)
                except UnicodeDecodeError as e:
                    logger.error(f"Error reading file {gripsbox_entry.name}: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Datei {gripsbox_entry.name}.")
            else:
                logger.error(f"File {gripsbox_entry.name} nicht gefunden.")
                raise HTTPException(status_code=404, detail=f"File {gripsbox_entry.name} nicht gefunden.")
    return file_contents


async def load_active_gripsbox_files(user_uuid: str) -> List[str]:
    """
    Load the contents of all active files in the user's Gripsbox, and load extracted text for PDFs.
    Includes the file name and type directly in the content.
    """
    user_gripsbox_path = get_users_gripsbox_folder(user_uuid)

    # Check if the Gripsbox folder exists
    if not os.path.exists(user_gripsbox_path):
        logger.error(f"Gripsbox folder {user_gripsbox_path} for user {user_uuid} does not exist.")
        raise HTTPException(status_code=404, detail="Gripsbox folder not found.")

    # Manually use get_db() for the session
    async for db in get_db():
        result = await db.execute(
            select(Gripsbox).where(Gripsbox.user == user_uuid, Gripsbox.active == True)
        )
        active_gripsboxes = result.scalars().all()

        if not active_gripsboxes:
            logger.warning(f"No active Gripsbox files found for user {user_uuid}.")
            raise HTTPException(status_code=404, detail=f"No active Gripsbox files found for user {user_uuid}")

        # Load content from all active files
        file_contents = []
        for gripsbox_entry in active_gripsboxes:
            file_path = os.path.join(user_gripsbox_path, gripsbox_entry.name)

            # If the file is a PDF, load the extracted text instead of the original file
            if gripsbox_entry.name.lower().endswith('.pdf'):
                # Check for the existence of the extracted text file
                extracted_text_filename = os.path.join(user_gripsbox_path, f"{os.path.splitext(gripsbox_entry.name)[0]}_extracted.txt")
                if os.path.exists(extracted_text_filename):
                    try:
                        with open(extracted_text_filename, "r", encoding="utf-8", errors="ignore") as text_file:
                            extracted_text = text_file.read()
                        # Append content with file name and type
                        file_contents.append(
                            f"File: {gripsbox_entry.name} (type: PDF)\n{extracted_text}"
                        )
                        logger.info(f"Loaded extracted text for PDF: {gripsbox_entry.name}")
                    except UnicodeDecodeError as e:
                        logger.error(f"Error reading extracted text for PDF {gripsbox_entry.name}: {str(e)}")
                        raise HTTPException(status_code=500, detail=f"Error reading extracted text for PDF {gripsbox_entry.name}.")
                else:
                    logger.warning(f"Extracted text file not found for PDF: {gripsbox_entry.name}")
            else:
                # For non-PDF files, load the content directly
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                            content = file.read()
                        # Append content with file name and type
                        file_contents.append(
                            f"File: {gripsbox_entry.name} (type: {gripsbox_entry.type})\n{content}"
                        )
                    except UnicodeDecodeError as e:
                        logger.error(f"Error reading file {gripsbox_entry.name}: {str(e)}")
                        raise HTTPException(status_code=500, detail=f"Error reading file {gripsbox_entry.name}.")
                else:
                    logger.error(f"File {gripsbox_entry.name} not found for user {user_uuid}.")
                    raise HTTPException(status_code=404, detail=f"File {gripsbox_entry.name} not found.")

        return file_contents





async def add_gripsbox_content_to_llm_context(user: User) -> List[Message]:
    """Load the active Gripsbox file contents and add them to the LLM context."""
    try:
        logger.debug(f"Loading active Gripsbox files for user {user.uuid}.")

        # Load the content of active Gripsbox files
        active_files_content = await load_active_gripsbox_files(user_uuid=str(user.uuid))

        # Create LLM context messages for each file
        llm_context = [
            Message(
                role="system",  # Treat as system message
                content=f"Content from Gripsbox file: {content}"
            ) for content in active_files_content
        ]


        return llm_context

    except Exception as e:
        logger.error(f"Error while adding Gripsbox content to LLM context: {str(e)}")
        raise HTTPException(status_code=500,
                            detail=f"Failed to add Gripsbox content to for user: {user.uuid} LLM context. {str(e)}")

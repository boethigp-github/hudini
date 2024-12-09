import fitz  # PyMuPDF
import logging
import os
from fastapi import HTTPException

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF file using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(pdf_path)  # Open the PDF file
        text = ""
        for page_num in range(len(doc)):  # Loop over all pages in the document
            page = doc.load_page(page_num)  # Get the page
            text += page.get_text("text")  # Extract text from the page
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

def extract_images_from_pdf(pdf_path: str, image_folder: str) -> list:
    """Extract images from a PDF and save them to a folder using PyMuPDF (fitz)."""
    try:
        doc = fitz.open(pdf_path)  # Open the PDF file
        image_filenames = []

        for page_num in range(len(doc)):  # Loop over all pages in the document
            page = doc.load_page(page_num)  # Get the page

            # Extract images from the page
            img_list = page.get_images(full=True)  # Get all images on the page
            for img_index, img in enumerate(img_list):
                xref = img[0]  # Reference to the image
                base_image = doc.extract_image(xref)  # Extract the image
                image_bytes = base_image["image"]  # Get image bytes

                # Generate file path for saving the image
                image_filename = os.path.join(image_folder, f"image_{page_num + 1}_{img_index + 1}.png")
                with open(image_filename, "wb") as img_file:
                    img_file.write(image_bytes)  # Save the image as PNG
                image_filenames.append(image_filename)  # Store the image filename

        return image_filenames
    except Exception as e:
        logger.error(f"Error extracting images from PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to extract images from PDF.")

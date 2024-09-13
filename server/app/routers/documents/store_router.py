from fastapi import APIRouter, HTTPException
from typing import List
import os
import fitz  # PyMuPDF for PDF extraction
from sentence_transformers import SentenceTransformer
import pickle  # For demonstration, you can use a more suitable vector database in practice
import logging

# Initialize the logger
logger = logging.getLogger("pdf_embeddings_router")

# Initialize the router
router = APIRouter()

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose another model

# Directory containing PDF files
PDF_DIRECTORY = "C:/projects/hudini/server/storage/pdfs"


# Function to extract text from a PDF
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        pdf_document = fitz.open(file_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        pdf_document.close()
    except Exception as e:
        logger.error(f"Error reading PDF file {file_path}: {str(e)}")
    return text


# Function to generate embeddings for a list of texts
def generate_embeddings(texts: List[str]) -> List[List[float]]:
    return model.encode(texts)


# Route to load PDFs, generate embeddings, and store them
@router.post("/process-pdfs")
async def process_pdfs():
    try:
        # List all PDF files in the directory
        pdf_files = [f for f in os.listdir(PDF_DIRECTORY) if f.endswith('.pdf')]

        if not pdf_files:
            raise HTTPException(status_code=404, detail="No PDF files found in the directory.")

        embeddings = []
        texts = []

        for pdf_file in pdf_files:
            file_path = os.path.join(PDF_DIRECTORY, pdf_file)
            text = extract_text_from_pdf(file_path)
            if text:
                texts.append(text)

        # Generate embeddings for the extracted texts
        embeddings = generate_embeddings(texts)

        # For demonstration, we'll save embeddings to a file
        with open("embeddings.pkl", "wb") as f:
            pickle.dump(embeddings, f)

        return {"detail": "PDFs processed and embeddings generated", "num_files": len(pdf_files)}

    except Exception as e:
        logger.error(f"Error processing PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing PDFs: {str(e)}")

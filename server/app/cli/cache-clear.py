import click
import os
import fitz  # PyMuPDF for PDF extraction
from sentence_transformers import SentenceTransformer
import pickle
from typing import List
from tqdm import tqdm

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')  # You can choose another model

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        pdf_document = fitz.open(file_path)
        for page in pdf_document:
            text += page.get_text()
        pdf_document.close()
    except Exception as e:
        click.echo(f"Error reading PDF file {file_path}: {str(e)}", err=True)
    return text

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    return model.encode(texts)

@click.command()
@click.argument('pdf_directory', type=click.Path(exists=True))
@click.option('--output', default='embeddings.pkl', help='Output file for embeddings')
def process_pdfs(pdf_directory: str, output: str):
    """Process PDFs and generate embeddings."""
    try:
        # List all PDF files in the directory
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

        if not pdf_files:
            click.echo("No PDF files found in the directory.", err=True)
            return

        texts = []

        # Process PDFs with progress bar
        with click.progressbar(pdf_files, label='Processing PDFs') as bar:
            for pdf_file in bar:
                file_path = os.path.join(pdf_directory, pdf_file)
                text = extract_text_from_pdf(file_path)
                if text:
                    texts.append(text)

        # Generate embeddings with progress bar
        click.echo("Generating embeddings...")
        embeddings = []
        chunk_size = 10  # Process 10 texts at a time to show progress
        for i in tqdm(range(0, len(texts), chunk_size), desc="Generating embeddings"):
            chunk = texts[i:i+chunk_size]
            chunk_embeddings = generate_embeddings(chunk)
            embeddings.extend(chunk_embeddings)

        # Save embeddings to a file
        with open(output, "wb") as f:
            pickle.dump(embeddings, f)

        click.echo(f"Embeddings saved to {output}")
        click.echo(f"Processed {len(pdf_files)} files.")

    except Exception as e:
        click.echo(f"An error occurred while processing PDFs: {str(e)}", err=True)

if __name__ == "__main__":
    process_pdfs()
import click
import os
import fitz  # PyMuPDF for PDF extraction
from sentence_transformers import SentenceTransformer
import pickle
from typing import List, Dict
from tqdm import tqdm
import datetime

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


def extract_text_and_metadata_from_pdf(file_path: str) -> Dict:
    try:
        pdf_document = fitz.open(file_path)
        text = ""
        metadata = {
            "filename": os.path.basename(file_path),
            "filepath": file_path,
            "creation_date": datetime.datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
            "modification_date": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
            "file_size": os.path.getsize(file_path),
            "num_pages": len(pdf_document),
            "pdf_metadata": pdf_document.metadata
        }

        for page in pdf_document:
            text += page.get_text()

        # Extract title (assuming the first non-empty line is the title)
        lines = text.split('\n')
        title = next((line.strip() for line in lines if line.strip()), "Untitled")
        metadata["extracted_title"] = title

        # Extract first 200 characters as a preview
        metadata["text_preview"] = text[:200].replace('\n', ' ').strip()

        pdf_document.close()
        return {"text": text, "metadata": metadata}
    except Exception as e:
        click.echo(f"Error processing PDF file {file_path}: {str(e)}", err=True)
        return {"text": "", "metadata": {}}


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    return model.encode(texts)


@click.command()
@click.argument('pdf_directory', type=click.Path(exists=True))
@click.option('--output', default='embeddings.pkl', help='Output file for embeddings')
@click.option('--metadata-output', default='metadata.pkl', help='Output file for metadata')
def process_pdfs(pdf_directory: str, output: str, metadata_output: str):
    """Process PDFs, generate embeddings, and extract metadata."""
    try:
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

        if not pdf_files:
            click.echo("No PDF files found in the directory.", err=True)
            return

        texts = []
        metadata_list = []

        with click.progressbar(pdf_files, label='Processing PDFs') as bar:
            for pdf_file in bar:
                file_path = os.path.join(pdf_directory, pdf_file)
                result = extract_text_and_metadata_from_pdf(file_path)
                if result["text"]:
                    texts.append(result["text"])
                    metadata_list.append(result["metadata"])

        click.echo("Generating embeddings...")
        embeddings = []
        chunk_size = 10
        for i in tqdm(range(0, len(texts), chunk_size), desc="Generating embeddings"):
            chunk = texts[i:i + chunk_size]
            chunk_embeddings = generate_embeddings(chunk)
            embeddings.extend(chunk_embeddings)

        with open(output, "wb") as f:
            pickle.dump(embeddings, f)

        with open(metadata_output, "wb") as f:
            pickle.dump(metadata_list, f)

        click.echo(f"Embeddings saved to {output}")
        click.echo(f"Metadata saved to {metadata_output}")
        click.echo(f"Processed {len(pdf_files)} files.")

    except Exception as e:
        click.echo(f"An error occurred while processing PDFs: {str(e)}", err=True)


if __name__ == "__main__":
    process_pdfs()
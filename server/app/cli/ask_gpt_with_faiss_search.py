import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import fitz  # PyMuPDF
import os
import logging
import pytesseract
from PIL import Image
import io
import shutil

# Konfiguration des Loggings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Überprüfen, ob Tesseract installiert ist
if shutil.which('tesseract') is None:
    logging.warning("Tesseract ist nicht im Systempfad. OCR wird möglicherweise nicht funktionieren.")

# Laden des Modells
model = SentenceTransformer('all-MiniLM-L6-v2')

# Laden des Faiss Index
index = faiss.read_index("dokumente_index.faiss")

# Laden der ursprünglichen Dokumente oder Metadaten
with open("metadata.pkl", "rb") as f:
    dokumente = pickle.load(f)

# Initialisieren des OpenAI-Clients
client = OpenAI(api_key='')  # Ersetzen Sie dies durch Ihren tatsächlichen API-Schlüssel

# Set zur Speicherung eindeutiger Dateipfade
unique_file_paths = set()


def log_file_path(file_path):
    if file_path not in unique_file_paths:
        unique_file_paths.add(file_path)
        logging.info(f"Neuer Dateipfad erfasst: {file_path}")


def suche(query_text, k=5):
    query_embedding = model.encode([query_text])[0]
    D, I = index.search(query_embedding.reshape(1, -1), k)

    results = []
    logging.info(f"Suchanfrage: '{query_text}'")
    logging.info("\nErgebnisse:")
    for i, (idx, dist) in enumerate(zip(I[0], D[0])):
        doc = dokumente[idx]
        file_path = doc.get('filepath', 'Unbekannter Pfad')
        log_file_path(file_path)
        result = {
            "document": doc,
            "similarity": 1 - dist
        }
        results.append(result)
        logging.info(f"{i + 1}. Dokument: {doc['filename']}")
        logging.info(f"   Pfad: {file_path}")
        logging.info(f"   Ähnlichkeit: {1 - dist:.4f}")

    return results


def extract_text_with_ocr(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text += pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logging.error(f"Fehler bei OCR-Verarbeitung: {str(e)}")
        return ""


def extract_full_text_from_pdf(file_path):
    try:
        log_file_path(file_path)
        if not os.path.exists(file_path):
            logging.error(f"Datei nicht gefunden: {file_path}")
            return ""

        logging.info(f"Öffne PDF: {file_path}")
        doc = fitz.open(file_path)

        # Log PDF structure
       # logging.info(f"PDF Struktur: {doc.metadata}")

        text = ""
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            ##logging.info(f"Seite {page_num + 1} extrahiert: {len(page_text)} Zeichen")
            text += page_text

        doc.close()



        return text
    except Exception as e:
        logging.error(f"Fehler beim Lesen der PDF-Datei {file_path}: {str(e)}")
        return ""


def extract_context(search_results, max_tokens=5000):
    context = ""
    for result in search_results:
        doc = result['document']
        filename = doc.get('filename', 'Unbekannte Datei')
        file_path = doc.get('filepath', '')
        log_file_path(file_path)

        context += f"Datei: {filename}\n"

        full_text = extract_full_text_from_pdf(file_path)
        preview = full_text[:max_tokens]

        context += f"Inhalt: {preview}\n\n"

        if len(context) > max_tokens:
            break
    return context[:max_tokens]


def query_llm(user_query, context):
    prompt = f"""
Basierend auf dem folgenden Inhalt eines Dokuments, beantworte bitte die Frage. 
Wenn der Inhalt verfügbar ist, gib bitte eine detaillierte Zusammenfassung oder die angefragten spezifischen Informationen.

Dokument-Inhalt:
{context}

Frage: {user_query}

Antwort:
"""

    try:

        logging.info(f"LLM-Anfrage: {prompt}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Du bist ein Assistent, der Dokumente analysiert und detaillierte Informationen daraus extrahiert. Wenn der Inhalt verfügbar ist, fasse ihn zusammen oder gib die angefragten spezifischen Details wieder."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Fehler bei der LLM-Anfrage: {str(e)}")
        return "Es ist ein Fehler bei der Verarbeitung Ihrer Anfrage aufgetreten. Bitte versuchen Sie es später erneut."


def answer_query(user_query, k=5):
    search_results = suche(user_query, k=k)
    context = extract_context(search_results)
    logging.info(f"Extrahierter Kontext (erste 2000 Zeichen): {context[:2000]}...")
    answer = query_llm(user_query, context)
    return answer


# Funktion zum Testen der Extraktion
def test_pdf_extraction(file_path):
    extracted_text = extract_full_text_from_pdf(file_path)

    logging.info(f"\nGesamtlänge des extrahierten Textes: {len(extracted_text)} Zeichen")


# Hauptausführung
if __name__ == "__main__":
    # Beispielanwendung
    user_query = "Zeige den Inhalt"
    answer = answer_query(user_query)
    logging.info(f"\nFrage: {user_query}")
    logging.info(f"Antwort: {answer}")

    # Test der PDF-Extraktion für ein spezifisches Dokument
    test_pdf_extraction(
        "C:/projects/hudini/server/storage/pdfs/Lebenslauf4.pdf")

    # Ausgabe aller eingelesenen Dateipfade
    logging.info("\nAlle eingelesenen Dateipfade:")
    for path in unique_file_paths:
        logging.info(path)

    # Interaktive Schleife
    while True:
        user_input = input("\nStellen Sie eine Frage (oder 'q' zum Beenden): ")
        if user_input.lower() == 'q':
            break
        answer = answer_query(user_input)
        logging.info(f"\nAntwort: {answer}")

    # Abschließende Ausgabe aller eingelesenen Dateipfade
    logging.info("\nAlle eingelesenen Dateipfade:")
    for path in unique_file_paths:
        logging.info(path)
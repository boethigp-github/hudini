import asyncio
import json
from langchain_community.utilities import SQLDatabase
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from urllib.parse import quote_plus
from sqlalchemy.exc import SQLAlchemyError
import warnings

# Deaktiviere Symlink-Warnungen
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Unterdrücke alle Warnungen
warnings.filterwarnings("ignore", category=FutureWarning)

async def main():
    username = "postgres"
    password = "postgres"
    host = "localhost"
    database = "hudini"
    db_uri = f"postgresql+psycopg2://{quote_plus(username)}:{quote_plus(password)}@{host}/{database}"

    def process_response(response_text, query_input):
        """Check if the model repeated the input and handle invalid responses."""
        if response_text.strip() == query_input.strip():
            return "The model repeated the input. No valid response generated."
        return response_text.strip()

    def format_response(response_text):
        """Format the response to match the desired structure."""
        try:
            formatted = []
            entries = response_text.split(",")
            for i in range(0, len(entries), 2):
                name = entries[i].strip().capitalize()
                role = entries[i + 1].strip().capitalize()
                formatted.append(f"Name: {name}, Role: {role}")
            return "; ".join(formatted)
        except Exception:
            return response_text  # Falls das Format nicht wie erwartet ist, wird die ursprüngliche Antwort zurückgegeben.

    try:
        # Verbinde mit der Datenbank
        print("Stelle Verbindung zur Datenbank her...")
        db = SQLDatabase.from_uri(
            db_uri,
            engine_args={"connect_args": {"client_encoding": "utf8"}}
        )
        print("Datenbankverbindung erfolgreich!")

        # Lade das TinyLlama-Modell
        print("Lade TinyLlama-Modell...")
        model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto"
        )

        # HuggingFace-Pipeline erstellen
        print("Erstelle HuggingFace-Pipeline...")
        pipeline_model = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=100,
            temperature=0.5,
            do_sample=True
        )

        # Beispielabfrage
        query_input = "Fetch all user details from the database and list them in plain text"
        print(f"Starte Abfrage: {query_input}")

        # Generiere Antwort mit dem Modell
        print("Generiere Antwort mit dem Modell...")
        inputs = tokenizer(query_input, return_tensors="pt").to("cuda")
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=100,
            temperature=0.1,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Überprüfe und formatiere die Antwort
        processed_response = process_response(response_text, query_input)
        formatted_response = format_response(processed_response)

        # JSON-Ausgabe
        result_json = {
            "query_input": query_input.strip(),
            "response_text": formatted_response
        }
        print(json.dumps(result_json, indent=4, ensure_ascii=False))

    except SQLAlchemyError as e:
        print(f"SQLAlchemy-Fehler: {str(e)}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    asyncio.run(main())

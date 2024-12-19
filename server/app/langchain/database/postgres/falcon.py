import asyncio
import json
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from urllib.parse import quote_plus
from sqlalchemy.exc import SQLAlchemyError
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

async def main():
    username = "postgres"
    password = "postgres"
    host = "localhost"
    database = "hudini"
    db_uri = f"postgresql+psycopg2://{quote_plus(username)}:{quote_plus(password)}@{host}/{database}"

    try:
        # Verbindung zur Datenbank herstellen
        print("Stelle Verbindung zur Datenbank her...")
        db = SQLDatabase.from_uri(
            db_uri,
            engine_args={"connect_args": {"client_encoding": "utf8"}}
        )
        print("LangChain-Datenbankverbindung erfolgreich!")

        # Lade das GPT-Neo-Modell
        print("Lade GPT-Neo-Modell...")
        model_name = "EleutherAI/gpt-neo-1.3B"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto"
        )

        # Erstelle eine HuggingFace-Pipeline mit `max_new_tokens` und höherem `max_length`
        print("Erstelle HuggingFace-Pipeline...")
        pipeline_model = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=700,  # Höheres Limit für die Gesamtlänge
            max_new_tokens=50,  # Begrenzung auf neue Tokens
            temperature=0.7,
        )

        # LangChain-kompatibles LLM
        from langchain.llms import HuggingFacePipeline
        llm = HuggingFacePipeline(pipeline=pipeline_model)

        # SQL-Agent erstellen
        print("Erstelle SQL-Agent...")
        sql_agent = create_sql_agent(llm=llm, db=db, verbose=True)

        # Beispielabfrage
        query_input = "Lese alle Benutzer aus der Datenbank im JSON-Format"
        print(f"Starte Abfrage: {query_input}")
        response = sql_agent.invoke({"input": query_input})
        print("Abfrage abgeschlossen!")

        # Strukturierte JSON-Ausgabe
        output = {
            "query_input": query_input,
            "response": response
        }
        print(json.dumps(output, indent=4, ensure_ascii=False))

    except SQLAlchemyError as e:
        print(f"SQLAlchemy-Fehler: {str(e)}")
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    asyncio.run(main())

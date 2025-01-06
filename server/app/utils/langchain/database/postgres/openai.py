import asyncio
import json
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import warnings

from server.app.routers.postcasts.elevenlabs.podcast_elevenlabs_router import OPENAI_API_KEY

warnings.filterwarnings("ignore", category=FutureWarning)
async def main():
    username = "postgres"
    password = "postgres"
    host = "localhost"
    database = "hudini"
    db_uri = f"postgresql+psycopg2://{quote_plus(username)}:{quote_plus(password)}@{host}/{database}"

    try:
        # Teste die Verbindung




        # Verbindung zur Datenbank herstellen

        db = SQLDatabase.from_uri(
            db_uri,
            engine_args={"connect_args": {"client_encoding": "utf8"}}
        )

        OPENAI_API_KEY = ""

        llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)

        sql_agent = create_sql_agent(llm=llm, db=db, verbose=True)


        query_input = "Lese alle Benutzer aus der Datenbank im Json format"
        response = sql_agent.invoke({"input": query_input})


        print(json.dumps(response, indent=4, ensure_ascii=False))

        # Extrahiere SQL und Ergebnis
        intermediate_steps = response.get("intermediate_steps", [])
        if intermediate_steps and len(intermediate_steps) > 0:
            sql_query = intermediate_steps[0].get("action_input", "N/A")
        else:
            sql_query = "Keine SQL-Abfrage gefunden"

        final_result = response.get("output", "Keine Ergebnisse gefunden")

        # Strukturierte JSON-Ausgabe
        output = {
            "query_input": query_input,
            "sql_query": sql_query,
            "result": final_result
        }


        print(json.dumps(output, indent=4, ensure_ascii=False))

    except SQLAlchemyError as e:
        print(f"Fehler bei der Verbindung: {str(e)}")
    except Exception as e:
        print(f"Fehler bei der Verbindung oder Abfrage: {e}")

if __name__ == "__main__":
    asyncio.run(main())

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Agent Language Model"
    LANGUAGE_DB_PATH: str = os.getenv("LANGUAGE_DB_PATH", "public/language_database/ingl_s.json")
    MEBRAIN_SYSTEM_API_URL: str = os.getenv(
        "MEBRAIN_SYSTEM_API_URL", "http://localhost:3005"
    )
    RAG_DECK_REFRESH_HOURS: int = int(os.getenv("RAG_DECK_REFRESH_HOURS", "24"))

settings = Settings()

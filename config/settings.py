from pathlib import Path

APP_NAME = "AI Job Bot"

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR}/database/jobs.db"

OPENAI_MODEL = "gpt-5"

MATCH_THRESHOLD = 80

DEFAULT_LOCATIONS = [
    "Bangalore",
    "Pune",
    "Hyderabad",
    "Remote"
]

DEFAULT_KEYWORDS = [
    "Application Support Engineer",
    "Production Support Engineer",
    "Blue Yonder",
    "Oracle SQL",
    "SCPO"
]
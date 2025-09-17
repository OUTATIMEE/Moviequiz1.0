import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent  # Es wird ein Path-Objekt angelegt, mit einem absoluten Verzeichnis in dem die Datei aktuell liegt
DATA_DIR = BASE_DIR / "data"    # erstellt ein Path-Objekt, mit data als Unterverzeichnis von BASE_DIR
DATA_DIR.mkdir(exist_ok=True)   # Dieses Unterverzeichnis wird erstellt, falls schon existiert gibt es keine Fehlermeldung

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR/'movies.sqlite3'}")  # die sql-datenbank wird unter data verzeichnis erstellt
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")    # der api-key ist über die Umgebungsvariabel TMDB_API_KEY abrufbar


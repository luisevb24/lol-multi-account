from pathlib import Path
import os

def load_env():
    BASE_DIR = Path(__file__).resolve().parent.parent
    ENV = BASE_DIR / ".env"

    if not ENV.is_file():
        return

    with open(ENV, "r") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            os.environ[key.strip()] = value.strip()






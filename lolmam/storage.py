import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "accounts.json"

def load_db():
    default_structure = {
    "next_id": 1,
    "accounts": []
    }
    if not DB_PATH.is_file():
        return default_structure
    
    with open(DB_PATH, "r") as f:
        json_data = json.load(f)

    return json_data

def save_db(db):
    DATA_DIR = BASE_DIR / "data"

    if not DATA_DIR.is_dir():
        os.mkdir(DATA_DIR)

    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)

def add_account(summoner_name: str, tag_line: str, region: str, puuid: str):
    db = load_db()

    acc_dict = {
        "id": db["next_id"],
        "summoner_name" : summoner_name,
        "tag_line" : tag_line,
        "region" : region,
        "puuid" : puuid,
    }

    db["accounts"].append(acc_dict)
    db["next_id"] += 1

    save_db(db)

    return acc_dict

def list_accounts():
    db = load_db()
    return db["accounts"]

def get_account(account_id):
    db = load_db()
    for acc in db["accounts"]:
        if acc["id"] == account_id:
            return acc
    return None
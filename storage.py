"""
storage.py
----------
Loads and saves all library data to one JSON file.

File layout:
{
    "books":        [ {id, title, author, category, total_copies, available_copies} ],
    "members":      [ {id, name, phone} ],
    "transactions": [ {id, book_id, member_id, issue_date, due_date,
                       return_date, fine} ]
}
return_date is null (None) while a book is still issued.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "library.json")


def empty_data():
    """Return a fresh, empty data structure."""
    return {"books": [], "members": [], "transactions": []}


def ensure_data_file():
    """Create the data folder and file if they do not exist yet."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(empty_data(), f, indent=4)


def load_data():
    """Load data from disk. If the file is corrupted, start fresh instead of crashing."""
    ensure_data_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in ("books", "members", "transactions"):
            if key not in data:
                raise ValueError("Missing key: " + key)
        return data
    except (json.JSONDecodeError, ValueError):
        print("Warning: data file was unreadable. Starting with empty data.")
        return empty_data()


def save_data(data):
    """Write the current data back to the JSON file."""
    ensure_data_file()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def next_id(records):
    """Return the next unused integer ID for a list of records."""
    if not records:
        return 1
    return max(r["id"] for r in records) + 1
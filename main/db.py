from pymongo import MongoClient
import time
from config import MONGO_URL

client = MongoClient(MONGO_URL)
db = client["rename_bot"]

settings_col = db["settings"]
thumbs_col = db["thumbnails"]
captions_col = db["captions"]
tasks_col = db["tasks"]
files_col = db["user_files"]

DEFAULT_SETTINGS = {
    "screenshot": True,
    "count": 3,
    "rename_type": "doc",
    "prefix_enabled": True,
    "prefix_text": "@sunriseseditsoffical6 -",
    "theme": "Light"
}

# ---------------- SETTINGS ----------------
def get_settings(user_id):
    data = settings_col.find_one({"_id": user_id})
    if not data:
        settings_col.insert_one({"_id": user_id, **DEFAULT_SETTINGS})
        return DEFAULT_SETTINGS.copy()

    for key, val in DEFAULT_SETTINGS.items():
        if key not in data:
            data[key] = val
            update_settings(user_id, key, val)
    return data

def update_settings(user_id, key, value):
    settings_col.update_one({"_id": user_id}, {"$set": {key: value}}, upsert=True)

def reset_settings(user_id):
    settings_col.update_one({"_id": user_id}, {"$set": DEFAULT_SETTINGS}, upsert=True)

# ---------------- THUMBNAIL ----------------
def set_thumbnail(user_id, file_id):
    thumbs_col.update_one({"_id": user_id}, {"$set": {"file_id": file_id}}, upsert=True)

def get_thumbnail(user_id):
    data = thumbs_col.find_one({"_id": user_id})
    return data["file_id"] if data else None

def clear_thumbnail(user_id):
    thumbs_col.delete_one({"_id": user_id})

# ---------------- CAPTION ----------------
def update_caption(user_id, text):
    captions_col.update_one({"_id": user_id}, {"$set": {"caption": text}}, upsert=True)

def get_caption(user_id):
    data = captions_col.find_one({"_id": user_id})
    return data["caption"] if data else None

# ---------------- TASKS ----------------
def get_user_tasks(user_id):
    data = tasks_col.find_one({"_id": user_id})
    return data["tasks"] if data else []

def add_task(user_id, task, username=None):
    """Add task and store username if provided."""
    update_data = {"$push": {"tasks": task}}
    if username:
        update_data["$set"] = {"username": username}
    tasks_col.update_one({"_id": user_id}, update_data, upsert=True)

def remove_task(user_id, index):
    data = get_user_tasks(user_id)
    if 0 <= index < len(data):
        task = data[index]
        tasks_col.update_one({"_id": user_id}, {"$pull": {"tasks": task}})
        return True
    return False

def get_all_user_tasks():
    """Return list of all users' tasks with IDs & usernames."""
    return list(tasks_col.find({}))

# ---------------- FILES ----------------
def save_file(user_id, file_name, file_path):
    files_col.update_one(
        {"_id": user_id},
        {"$push": {"files": {
            "name": file_name,
            "path": file_path,
            "time": time.time()
        }}},
        upsert=True
    )

def get_saved_file(user_id, filename):
    user_data = files_col.find_one({"_id": user_id})
    if not user_data:
        return None
    for file in user_data.get("files", []):
        if file["name"] == filename:
            return file["path"]
    return None

def get_user_files(user_id):
    data = files_col.find_one({"_id": user_id})
    return data.get("files", []) if data else []

def clear_user_files(user_id):
    files_col.delete_one({"_id": user_id})

# ---------------- CLEAR DB ----------------
def clear_database():
    settings_col.drop()
    thumbs_col.drop()
    captions_col.drop()
    tasks_col.drop()
    files_col.drop()

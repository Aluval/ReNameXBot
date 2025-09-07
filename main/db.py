from pymongo import MongoClient
import time
from config import MONGO_URL

#ALL FILES UPLOADED - CREDITS 🌟 - @Sunrises_24
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

# Get all tasks of a user
def get_user_tasks(user_id):
    data = tasks_col.find_one({"_id": user_id})
    return data["tasks"] if data else []

# Add a task for a user (store only user_id)
def add_task(user_id, task):
    """
    task: dict with {"filename": ..., "file_id": ...}
    """
    tasks_col.update_one({"_id": user_id}, {"$push": {"tasks": task}}, upsert=True)

# Remove a task by file_id or filename
def remove_task(user_id, identifier):
    """
    Remove task either by file_id or filename
    identifier: str (file_id or filename)
    """
    user = tasks_col.find_one({"_id": user_id})
    if not user:
        return False

    tasks = user.get("tasks", [])
    new_tasks = [
        task for task in tasks
        if not (
            (isinstance(task, dict) and (task.get("file_id") == identifier or task.get("filename") == identifier))
            or (isinstance(task, str) and task == identifier)
        )
    ]

    if len(new_tasks) != len(tasks):
        tasks_col.update_one({"_id": user_id}, {"$set": {"tasks": new_tasks}})
        return True
    return False

# Get all tasks for all users
def get_all_user_tasks():
    return list(tasks_col.find({}, {"_id": 1, "tasks": 1}))

# ---------------- FILES ----------------

def save_file(user_id, file_name, file_id):
    files_col.update_one(
        {"_id": user_id},
        {"$push": {"files": {"name": file_name, "file_id": file_id, "time": time.time()}}},
        upsert=True
    )

def get_saved_file(user_id, filename):
    user_data = files_col.find_one({"_id": user_id})
    if not user_data:
        return None
    for file in user_data.get("files", []):
        if file["name"] == filename:
            return file.get("file_id")
    return None

def get_user_files(user_id):
    data = files_col.find_one({"_id": user_id})
    if not data:
        return []
    return [f for f in data.get("files", []) if "file_id" in f]

def clear_user_files(user_id):
    files_col.delete_one({"_id": user_id})

# ---------------- CLEAR DB ----------------
def clear_database():
    settings_col.drop()
    thumbs_col.drop()
    captions_col.drop()
    tasks_col.drop()
    files_col.drop()






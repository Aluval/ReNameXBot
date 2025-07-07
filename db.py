from pymongo import MongoClient

MONGO_URL = "mongodb+srv://HARSHA24:HARSHA24@cluster0.sxaj8up.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URL)

db = client["rename_bot"]
settings_col = db["settings"]
thumbs_col = db["thumbnails"]
captions_col = db["captions"]
admin_col = db["admins"]

DEFAULT_SETTINGS = {
    "screenshot": True,
    "count": 3,
    "rename_type": "doc",
    "prefix_enabled": True,
    "prefix_text": "@sunriseseditsoffical6 -"
}

def get_settings(user_id):
    data = settings_col.find_one({"_id": user_id})
    if not data:
        settings_col.insert_one({"_id": user_id, **DEFAULT_SETTINGS})
        return DEFAULT_SETTINGS.copy()
    return data

def update_settings(user_id, key, value):
    settings_col.update_one({"_id": user_id}, {"$set": {key: value}}, upsert=True)

def set_thumbnail(user_id, file_id):
    thumbs_col.update_one({"_id": user_id}, {"$set": {"file_id": file_id}}, upsert=True)

def get_thumbnail(user_id):
    data = thumbs_col.find_one({"_id": user_id})
    return data["file_id"] if data else None

def clear_thumbnail(user_id):
    thumbs_col.delete_one({"_id": user_id})

def update_caption(user_id, text):
    captions_col.update_one({"_id": user_id}, {"$set": {"caption": text}}, upsert=True)

def get_caption(user_id):
    data = captions_col.find_one({"_id": user_id})
    return data["caption"] if data else None

def get_admins():
    return [admin["_id"] for admin in admin_col.find()]

def is_admin_user(user_id):
    return admin_col.find_one({"_id": user_id}) is not None

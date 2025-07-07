from pymongo import MongoClient

# 🧠 MongoDB Setup
MONGO_URL = "mongodb+srv://HARSHA24:HARSHA24@cluster0.sxaj8up.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # or your Atlas URI

client = MongoClient(MONGO_URL)
db = client.rename_bot
collection = db.users

def get_settings(user_id: int) -> dict:
    user = collection.find_one({"id": user_id})
    if not user:
        default = {
            "id": user_id,
            "screenshot": False,
            "count": 3,
            "prefix_enabled": True,
            "prefix_text": "@sunriseseditsoffical6 -",
            "rename_type": "doc",  # "video" or "doc"
            "caption_style": "bold",  # bold, italic, code, mono, plain
            "thumbnail": None
        }
        collection.insert_one(default)
        return default
    return user

def update_settings(user_id: int, key: str, value):
    collection.update_one({"id": user_id}, {"$set": {key: value}})

def set_thumbnail(user_id: int, file_id: str):
    update_settings(user_id, "thumbnail", file_id)

def get_thumbnail(user_id: int) -> str | None:
    user = get_settings(user_id)
    return user.get("thumbnail")

def clear_thumbnail(user_id: int):
    update_settings(user_id, "thumbnail", None)

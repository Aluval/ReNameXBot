from pymongo import MongoClient

# 🧠 MongoDB Setup
MONGO_URL = "mongodb+srv://HARSHA24:HARSHA24@cluster0.sxaj8up.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # or your Atlas URI

client = MongoClient(MONGO_URL)
db = client["RenameBot"]
col = db["users"]

def get_settings(user_id):
    data = col.find_one({"_id": user_id})
    if not data:
        default = {
            "_id": user_id,
            "screenshot": False,
            "count": 3,
            "prefix": True,
            "rename_type": "doc",
            "caption_style": "bold",
            "thumb": None
        }
        col.insert_one(default)
        return default
    return data

def update_settings(user_id, key, value):
    col.update_one({"_id": user_id}, {"$set": {key: value}}, upsert=True)

def set_thumbnail(user_id, file_id):
    update_settings(user_id, "thumbnail", file_id)

def get_thumbnail(user_id):
    user = get_settings(user_id)
    return user.get("thumbnail")

def clear_thumbnail(user_id):
    update_settings(user_id, "thumbnail", None)

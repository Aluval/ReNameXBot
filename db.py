from pymongo import MongoClient

# 🧠 MongoDB Setup
MONGO_URL = "mongodb+srv://HARSHA24:HARSHA24@cluster0.sxaj8up.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # or your Atlas URI
client = MongoClient(MONGO_URL)
db = client.rename_bot_db
settings_col = db.user_settings

# 🔍 Get User Settings
def get_settings(user_id):
    user = settings_col.find_one({"_id": user_id})
    if not user:
        default = {
            "_id": user_id,
            "screenshot": False,
            "count": 3,
            "prefix": True,
            "caption_style": "bold",
            "thumb_id": None,
            "rename_type": "doc"
        }
        settings_col.insert_one(default)
        return default
    return user

# 🔁 Update a Specific Setting
def update_settings(user_id, key, value):
    settings_col.update_one({"_id": user_id}, {"$set": {key: value}}, upsert=True)

# 📌 Thumbnail Management
def set_thumbnail(user_id, file_id):
    update_settings(user_id, "thumb_id", file_id)

def get_thumbnail(user_id):
    return get_settings(user_id).get("thumb_id")

def clear_thumbnail(user_id):
    update_settings(user_id, "thumb_id", None)

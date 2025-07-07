from pymongo import MongoClient

MONGO_URL = "mongodb+srv://HARSHA24:HARSHA24@cluster0.sxaj8up.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # or your Atlas URI
client_mongo = MongoClient(MONGO_URL)
db = client_mongo.rename_bot_db
user_settings = db.user_settings


def get_settings(user_id):
    user = user_settings.find_one({"_id": user_id})
    if not user:
        return {"screenshot": False, "count": 3}
    return user


def update_settings(user_id, key, value):
    user_settings.update_one({"_id": user_id}, {"$set": {key: value}}, upsert=True)

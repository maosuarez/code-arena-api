from passlib.context import CryptContext
import random
import string
from bson import ObjectId

def sanitize_user_dict(db_user: dict) -> dict:
    user_copy = db_user.copy()
    if "_id" in user_copy and isinstance(user_copy["_id"], ObjectId):
        user_copy["_id"] = str(user_copy["_id"])
    return user_copy

def generate_unique_code(existing_codes: set, length: int = 6) -> str:
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if code not in existing_codes:
            return code

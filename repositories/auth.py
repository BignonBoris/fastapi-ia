from config import DB

async def loginRepo(email : str):
    user = await DB.users.find_one({"email" : email}, {"_id": 0}) 
    if user:
        # user["email"] = "" if user.get("email") == user.get("user_id") else user.get("email")
        return user
    else :
        return None


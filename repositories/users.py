from config import DB
from models.models import UserInput
import uuid

async def getUsersRepo():
    users = DB.users.find({}, {"_id": 0}).sort("_id", -1)
    return await users.to_list(length=None)


async def getUserRepo(user_id : str):
    return await DB.users.find_one({"user_id" : user_id}, {"_id": 0}) 


async def createUserRepo(data : UserInput): 
    unique_code = str(uuid.uuid4())
    await DB.users.insert_one({
        "user_id" : unique_code,
        "email" : unique_code, 
        "name" : data.name, 
        "age" : data.age,
        "sexe" : data.sexe,
        # "country" : data.country,
    })

    return unique_code

async def updateUserRepo(user_id: str, data: UserInput):
    await DB.users.update_one(
            {"user_id": user_id},              # Filtre
            {"$set": {"name": data.name,  "age" : data.age, "sexe" : data.sexe,} }     # Action
        )
    
    return user_id

async def deleteUserRepo(user_id : str):
    result = await DB.users.delete_one({"user_id" : user_id}) 
    return result.deleted_count
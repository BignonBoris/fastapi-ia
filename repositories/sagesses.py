from config import DB
from models.models import UserInput
import uuid


async def getSagessesRepo(user_id : str):
    return await DB.sagesses.find_one({"user_id" : user_id}, {"_id": 0}) 


async def createSagessesRepo(user_id: str , sagesses = []): 
    unique_code = str(uuid.uuid4())
    await DB.sagesses.insert_one({
        "sagesse_id" : unique_code,
        "user_id" : user_id,
        "sagesses" : sagesses,
    })

    return unique_code

async def updateSagessesRepo(user_id: str, sagesses):
    await DB.sagesses.update_one(
            {"user_id": user_id},              # Filtre
            {"$set": {"sagesses": sagesses,} }     # Action
        )
    
    return user_id

async def deleteUserRepo(user_id : str):
    result = await DB.users.delete_one({"user_id" : user_id}) 
    return result.deleted_count
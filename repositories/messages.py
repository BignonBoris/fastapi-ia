from config import DB
import uuid
from models.models import MessageInput

async def getMessagesByUserRepo(user_id : str):
    userMessages = await DB.messages.find_one({"user_id" : user_id}, {"_id": 0})
    return [] if not userMessages else userMessages.get("messages")


async def createMessagesRepo(user_id : str, data : MessageInput = []): 
    unique_code = str(uuid.uuid4())
    await DB.messages.insert_one({
        "user_id" : user_id,
        "message_id" : unique_code, 
        "messages" : [] if not data else data.get("messages"),
        # "name" : data.name,
    })

    return unique_code


async def updateMessagesRepo(user_id : str, data : MessageInput):
    await DB.messages.update_one(
            {"user_id": user_id},              # Filtre
            {"$set": {"messages": data.get("messages"),} }     # Action
        )
    
    return user_id


async def deleteMessagesRepo(user_id : str):
    result = await DB.messages.delete_one({"user_id" : user_id}) 
    return result.deleted_count
from config import DB
from models.models import UserInput
import uuid

async def getUsersRepo():
    users = DB.users.find({}, {"_id": 0}).sort("_id", -1)
    return await users.to_list(length=None)


async def getUserRepo(searchValue : str , searchKey : str = "user_id"):
    user = await DB.users.find_one({searchKey : searchValue}, {"_id": 0}) 
    user["email"] = "" if user.get("email") == user.get("user_id") else user.get("email")
    return user


async def createUserRepo(data : UserInput): 
    unique_code = str(uuid.uuid4())
    await DB.users.insert_one({
        "user_id" : unique_code,
        "email" : unique_code, 
        "name" : data.name, 
        "age" : data.age,
        "sexe" : data.sexe,
        "fcmToken" : data.fcmToken,
        "profileImagePath" : data.profileImagePath,
        "country" : data.country,
    })

    return unique_code

async def updateUserRepo(user_id: str, data: UserInput):
    user = await getUserRepo(user_id)
    await DB.users.update_one(
            {"user_id": user_id},              # Filtre
            {"$set": {
                "pseudo": data.pseudo if data.pseudo  else user.get("pseudo"),
                "country": data.country if data.country  else user.get("country"),
                "phone": data.phone if data.phone  else user.get("phone"),
                "dateOfBirth": data.dateOfBirth if data.dateOfBirth else user.get("dateOfBirth"),
                "sexe": data.sexe if data.sexe else user.get("sexe"),  
                "occupation" : data.occupation if data.occupation else user.get("occupation"), 
                "email" : data.email if data.email else user.get("email") if user.get("email") else user_id,
                "password" : data.password if data.password else user.get("password"),
                "name" : data.name if data.name else user.get("name"),
                "age" : data.age if data.age else user.get("age"),
                "fcmToken" : data.fcmToken if data.fcmToken else user.get("fcmToken"),
                "profileImagePath" : data.profileImagePath if data.profileImagePath else user.get("profileImagePath"),
                } 
            }     # Action
        )
    
    return user_id

async def deleteUserRepo(user_id : str):
    result = await DB.users.delete_one({"user_id" : user_id}) 
    return result.deleted_count
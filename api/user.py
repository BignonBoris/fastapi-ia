from fastapi import APIRouter  
from models.models import UserInput
from repositories.users import updateUserRepo, createUserRepo, getUserRepo

user_router = APIRouter(prefix="/user",tags=["user"] )  
  

@user_router.post("")
async def createUser(input: UserInput):
    return await createUserRepo(input)
    
@user_router.get("/{user_id}")
async def getUser(user_id: str): 
    return await getUserRepo(user_id)

@user_router.put('/{user_id}')
async def updateUser(user_id : str,input : UserInput):
    return await updateUserRepo(user_id, input)


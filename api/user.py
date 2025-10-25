from fastapi import APIRouter  
from models.models import UserInput
from repositories.users import updateUserRepo

user_router = APIRouter(prefix="/user",tags=["user"] )  
  

@user_router.put('/{user_id}')
async def updateUser(user_id : str,input : UserInput):
    return await updateUserRepo(user_id, input)


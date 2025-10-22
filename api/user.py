from fastapi import APIRouter
from config import MONGO_URI
from data.matching import prompt_matching, build_matching_prompt
from models.models import UserInput, ChatInput 
import json
from repositories.groq import groqApi
from models.models import MachingInput, MachingGuestInput, UpdateMachingGuestInput, ConnexionMessageInput
from repositories.users import getUserRepo, updateUserRepo

user_router = APIRouter(prefix="/user",tags=["user"] )  
  

@user_router.put('/{user_id}')
async def updateUser(user_id : str,input : UserInput):
    return await updateUserRepo(user_id, input)


from fastapi import APIRouter  
from models.models import AuthInput
from repositories.users import updateUserRepo, createUserRepo, getUserRepo

auth_router = APIRouter(prefix="/auth",tags=["Auth"] )  
  

@auth_router.post("/login")
async def authLogin(input: AuthInput):
    return await getUserRepo(input.email, searchKey = "email")
from fastapi import APIRouter  
from models.models import AuthInput
from repositories.auth import loginRepo

auth_router = APIRouter(prefix="/auth",tags=["Auth"] )  
  

@auth_router.post("/login")
async def authLogin(input: AuthInput):
    return await loginRepo(input.email)
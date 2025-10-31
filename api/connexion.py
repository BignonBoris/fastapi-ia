from fastapi import APIRouter
from models.models import ConexionInput
from repositories.matching import createConnexionRepo

connexion_router = APIRouter(prefix="/connexion",tags=["Connexion"] )  

@connexion_router.post("/scanner")
async def scanner(input: ConexionInput):
    return await createConnexionRepo("scanner", input.user_id, input.guest_id)
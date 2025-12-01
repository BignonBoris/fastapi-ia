from fastapi import APIRouter, File, UploadFile
from models.models import ConnexionInput, ConnexionMessageInput
from repositories.matching import createConnexionRepo ,  updateConnexionRepo
from repositories.connexion import connexionLoginRepo ,  connexionLogOutRepo
from config import API_URL
import shutil
import uuid
import os

connexion_router = APIRouter(prefix="/connexion",tags=["Connexion"] )  


UPLOAD_DIR = API_URL+"uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  


@connexion_router.post("/scanner")
async def scanner(input: ConnexionInput):
    return await createConnexionRepo("scanner", input.user_id, input.guest_id)

    
@connexion_router.get("/login/{connexion_id}/{id}")
async def connexion_login(connexion_id : str, id : str):
    update_id = await connexionLoginRepo(connexion_id, id)
    return update_id

@connexion_router.get("/logout/{connexion_id}/{id}")
async def connexion_logout(connexion_id : str, id : str):
    update_id = await connexionLogOutRepo(connexion_id, id)
    return update_id


@connexion_router.post("/message/upload-image/{connexion_id}")
async def upload_image(connexion_id: str,  user_id : str, file : UploadFile = File()):
    # Crée un nom de fichier unique

    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Sauvegarde le fichier
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        
    public_url = f"{API_URL}uploads/{filename}"

    image_url = f"/{file_path}"  # ou une URL Cloud
    
    update_id = await updateConnexionRepo(connexion_id, ConnexionMessageInput(user_id = user_id, message = public_url, type = "IMAGE"))
    
    # update_id = await updateUserRepo(user_id, UserInput(profileImagePath = public_url))

    return {"path" : image_url, "public_url" : public_url, "update_id" : update_id}

    return JSONResponse({
        "message": "Image uploaded successfully",
        "image_url": image_url
    })
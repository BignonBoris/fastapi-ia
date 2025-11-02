from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from models.models import UserInput
from repositories.users import updateUserRepo, createUserRepo, getUserRepo
import shutil
import uuid
import os

user_router = APIRouter(prefix="/user",tags=["user"] )

baseUrl = "https://fastapi-ia-74eo.onrender.com"
# baseUrl = "http://127.0.0.1:8000"

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)  

@user_router.post("")
async def createUser(input: UserInput):
    return await createUserRepo(input)
    
@user_router.get("/{user_id}")
async def getUser(user_id: str): 
    return await getUserRepo(user_id)

@user_router.put('/{user_id}')
async def updateUser(user_id : str,input : UserInput):
    return await updateUserRepo(user_id, input)

@user_router.post("/upload-profile-image/{user_id}")
async def upload_profile_image(user_id: str, file: UploadFile = File(...)):
    # Crée un nom de fichier unique
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Sauvegarde le fichier
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

        
    public_url = f"{baseUrl}/uploads/{filename}"

    image_url = f"/{file_path}"  # ou une URL Cloud

    # # Mets à jour l'utilisateur dans MongoDB
    # users.update_one(
    #     {"user_id": user_id},
    #     {"$set": {"image": image_url}}
    # )

    return {"path" : image_url, "url" : public_url}

    return JSONResponse({
        "message": "Image uploaded successfully",
        "image_url": image_url
    })
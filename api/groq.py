from groq import Groq, AuthenticationError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, MONGO_URI
from data.llama import build_system_prompt 
from data.groq import matching_system_prompt
from models.models import UserInput, ChatInput
from motor.motor_asyncio import AsyncIOMotorClient
import json
import uuid
from types import SimpleNamespace
from repositories.users import getUsersRepo, getUserRepo, createUserRepo, updateUserRepo, deleteUserRepo
from repositories.messages import getMessagesByUserRepo, updateMessagesRepo, createMessagesRepo, deleteMessagesRepo
from repositories.sagesses import getSagessesRepo, createSagessesRepo, updateSagessesRepo
from repositories.groq import groqApi

groq_router = APIRouter(prefix="/groq",tags=["groq"] ) 

groqClient = Groq(api_key=GROQ_API_KEY,)

mongoClient = AsyncIOMotorClient(MONGO_URI)
db = mongoClient.sample_mflix  # Nom de ta base

# Initialiser l’historique de conversation
chat_history = [ ]
sagesses_history = []


async def getInitAssistantPrompt (user_id: str):
    userItem = await getUserRepo(user_id)

    system_prompt = build_system_prompt(SimpleNamespace(**{ "name" : "", "age" : "", "sexe" : "", })) 

    if userItem:
        system_prompt = build_system_prompt(SimpleNamespace(**{
            "name" : userItem.get("name"),
            "age" : userItem.get("age"),
            "sexe" : userItem.get("sexe"),
            # "country" : userItem.get("country"),
        })) 
    
    return system_prompt  


def getInitUserPrompt():
    return """ 
                Salut l'utilisateur et parle lui de toi en maximum 30 mots et pose moi une question pour commencer
            """

def getInitUserSagessePrompt(sagesses = []):
    return f"""En te basant sur nos échanges précédents, et en conservant ton rôle de conseiller matrimonial :
                Fournis une sagesse pertinente pour aider l'utilisateur à mieux gérer sa situation amoureuse actuelle.
                Il t'a déjà demandé des sagesses, voici celles que tu as déjà données:
                {chr(10).join(["- " + s.get("sagesse") for s in sagesses]) if sagesses else "Aucune sagesse pour l'instant"}
                Ta réponse doit inclure une explication claire et la leçon à retenir.
                Le tout doit être structuré **exclusivement** au format JSON avec les clés suivantes :
                {{"sagesse", "explanation", "lesson"}}
                **Ne retourne que le JSON. Aucun autre texte n'est autorisé.**
            """


@groq_router.get("/users")
async def getUsers(): 
    return await getUsersRepo()

@groq_router.put("/user/{user_id}")
async def updateUser(user_id: str, input: UserInput):
    return await updateUserRepo(user_id, input) 

@groq_router.delete("/user/{user_id}")
async def deleteUser(user_id : str):
    return await deleteUserRepo(user_id)


@groq_router.get("/messages/{user_id}")
async def getUserMessages(user_id : str):

    global chat_history
    
    chat_history = await getMessagesByUserRepo(user_id) if not chat_history else chat_history
    
    return chat_history[2:]


@groq_router.get("/messages/init/{user_id}")
async def initUserMessage(user_id: str):
    
    global chat_history
    
    chat_history = [{"role": "assistant", "content": await getInitAssistantPrompt(user_id) }]
    chat_history.append({"role": "user", "content": getInitUserPrompt()}) 
    response = await groqApi(chat_history)
    chat_history = response.get("messages") 
    update_message = await updateMessagesRepo(user_id, {"messages": chat_history})
    
    return chat_history[2:]


@groq_router.post("/messages/{user_id}")
async def createMessages(user_id : str):
    messages = [{"role": "assistant", "content": await getInitAssistantPrompt(user_id) },
                {"role": "user", "content": getInitUserPrompt()}]
    return await createMessagesRepo(user_id, {"messages": messages})


@groq_router.delete("/messages/{user_id}")
async def deleteMessages(user_id : str):
    return await deleteMessagesRepo(user_id)
     

@groq_router.post("/messages/add/{user_id}")
async def addMessage(user_id: str , input: ChatInput): 
    
    global chat_history
    # Ajouter le message utilisateur à l'historique
    chat_history.append({"role": "user", "content": input.message})
    response = await groqApi(chat_history)
    await updateMessagesRepo(user_id, {"messages": response.get("messages")})

    return response.get("message")
    
#API DE CREATION DE LA TABLE SAGESSE
@groq_router.post("/sagesses/{user_id}")
async def createSagesses(user_id : str):
    return await createSagessesRepo(user_id)

#API DE CREATION DE LA TABLE SAGESSE SI LA TABLE N'EXISTE PAS ENCORE ET INITIALISER AVEC UNE PREMIERE SAGESSE
@groq_router.get("/sagesses/init/{user_id}")
async def initSagesses(user_id : str):
    global chat_history
    sagesses = chat_history.copy()
    
    sagesse =  await createSagessesRepo(user_id)
     
    sagesses.append({ "role": "user", "content" : getInitUserSagessePrompt([]) })

    # Appel à l'API
    response = await groqApi(sagesses)

    response = json.loads(response.get("message"))
    sagesses_history.append(response)

    updateRep = await updateSagessesRepo(user_id, sagesses_history)
    
    return response


@groq_router.get("/sagesses/{user_id}")
async def getSagesses(user_id: str):
    sagesses =  await getSagessesRepo(user_id)
    return sagesses if not sagesses else sagesses.get("sagesses")[-1]


@groq_router.get("/sagesses/new/{user_id}")
async def getNewSagesse(user_id: str):

    global sagesses_history
    global chat_history
    sagesses = chat_history.copy()
    
    if not sagesses_history:
        sagessesList = await getSagessesRepo(user_id)
        sagesses_history = [] if not sagessesList else sagessesList.get("sagesses")
        
    sagesses.append({ "role": "user", "content" : getInitUserSagessePrompt(sagesses_history) })

    # Appel à l'API
    response = await groqApi(sagesses)

    response = json.loads(response.get("message"))
    sagesses_history.append(response)
    updateRep = await updateSagessesRepo(user_id, sagesses_history)
    
    return response


@groq_router.get("/sms/{user_id}")
async def getSms(user_id: str):
    
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    historical = []
    
    if conversationItem: 
        historical = conversationItem.get("messages")
    else:
        historical = [{"role": "assistant", "content": await getInitAssistantPrompt(user_id) }]
    
    
    historical.append({
        "role": "user",
        "content" : """Agis comme un assistant romantique expert en communication amoureuse.
                    Génère un message amoureux unique et sincère qui pourrait être envoyé à un partenaire pour renforcer ou raviver les sentiments.
                    Le message doit être élégant, respectueux et chaleureux.
                    Pour chaque proposition :
                    message → une phrase ou un court paragraphe exprimant l’émotion (tu peux utiliser des icônes, le formatage gras ou italique si nécessaire).
                    moment → une liste non ordonnée (- élément) contenant 3 moments précis où ce message peut être envoyé.
                    reaction → une liste non ordonnée (- élément) contenant 3 effets recherchés ou réactions attendues de la personne qui reçoit ce message.
                    Structure de sortie obligatoire : retourne uniquement un JSON au format suivant, sans aucun texte autour :
                    { 
                    "message": "...",
                    "moment": [ "- ...", "- ...", "- ..." ],
                    "reaction": [ "- ...", "- ...", "- ..." ]
                    }
                    """
        })
    
    # Appel à l'API
    response = groqClient.chat.completions.create(
        model=GROQ_MODEL,  # ou autre modèle Groq
        messages=historical,
        temperature=TEMPERATURE,
    )
    response = response.choices[0].message.content
    
    print(response)
    return json.loads(response)

@groq_router.get("/matching/{user_id}")
async def getMatching(user_id: str):
    conversationItem = await db.projets.find_one({"user_id" : user_id})
    userMessages = conversationItem.get("messages") if conversationItem else "" 
    projects = await db.projets.find({}, {"_id": 0}).sort("_id", -1).limit(5).to_list(length=None)
    resultat = []
    for project in projects:
        # print(project.get('messages')[2:])
        response = groqClient.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": matching_system_prompt},
                {"role": "user", "content": f"Historique utilisateur A : {userMessages[2:] }"},
                {"role": "user", "content": f"Historique utilisateur B : {project.get('messages')[2:] }"}
            ]
        )
        return json.loads(response.choices[0].message.content)
        resultat.append(json.loads(response.choices[0].message.content))
        
    return resultat
from fastapi import APIRouter
from config import MONGO_URI
from data.matching import build_system_prompt , prompt_matching, build_matching_prompt
from data.groq import matching_system_prompt
from models.models import UserInput, ChatInput
from motor.motor_asyncio import AsyncIOMotorClient
import json
from types import SimpleNamespace
from repositories.groq import groqApi
from models.models import MachingInput, MachingGuestInput, UpdateMachingGuestInput, ConnexionMessageInput
from repositories.matching import (createMatchingRepo, getMatchingByUserRepo, getMatchingRepo, updateMatchingRepo,
                                   getUsersWithHighScore, 
                                   createGuestInvitationRepo, getMatchingInvitationRepo, updateGuestInvitationRepo, getInvitationsRepo,
                                   createConnexionRepo, getAllUserConnexionsRepo, getConnexionRepo, updateConnexionRepo )

matching_router = APIRouter(prefix="/matching",tags=["matching"] )  

mongoClient = AsyncIOMotorClient(MONGO_URI)
db = mongoClient.sample_mflix  # Nom de ta base

# Initialiser l’historique de conversation
chat_history = []


async def getInitPrompt (user_id: str):
    userItem = await db.users.find_one({"user_id" : user_id})

    system_prompt = build_system_prompt(SimpleNamespace(**{ "name" : "", "age" : "", "sexe" : "", })) 

    if userItem:
        system_prompt = build_system_prompt(SimpleNamespace(**{
            "name" : userItem.get("name"),
            "age" : userItem.get("age"),
            "sexe" : userItem.get("sexe"),
            # "country" : userItem.get("country"),
        })) 
    
    return system_prompt

histories = [{"role": "system", "content": prompt_matching()}, ]
savedata = []


async def getMatchingNextQuestion(response):
    try:
        message = response.get("message")
        data = json.loads(message)
        # messageIA = data["messageIA"]

    except json.JSONDecodeError as e:
        print("❌ Erreur de parsing JSON :", e) 
        data = []

    except AttributeError as e:
        print("❌ Erreur de parsing AttributeError :", e) 
        data = []

    return data


@matching_router.get("/{matching_id}")
async def getMatching(matching_id: str):
    matching = await getMatchingRepo(matching_id)
    return matching

    
@matching_router.get("/messages/{user_id}")
async def getAllMatchingMessage(user_id: str):
    matching = await getMatchingByUserRepo(user_id)
    return matching["messages"] if matching else []



@matching_router.get('/init/{user_id}')
async def initMatching(user_id: str):
    
    histories = [{"role": "system", "content": prompt_matching()}, ]
    savedata = []
    
    response = await groqApi(histories)
    userMatchingItem = await getMatchingByUserRepo(user_id)

    data = await getMatchingNextQuestion(response)

    messageIA = data["messageIA"] if data else ""

    if data:
        assistance = {"role": "assistant", "content": messageIA}
        savedata.append(assistance)

        if not userMatchingItem:
            await createMatchingRepo(user_id, savedata)
        else:
            await updateMatchingRepo(user_id, messages = savedata, score = data["score"], resume=data["resume"] )

    return messageIA



@matching_router.post('/message/{user_id}')
async def test(user_id : str, data : MachingInput):

    histories = [{"role": "system", "content": prompt_matching()}, ]
    savedata = []

    userMatchingItem = await getMatchingByUserRepo(user_id)
    if userMatchingItem:
        savedata = userMatchingItem.get('messages')
        histories = histories + savedata
 
    histories.append({"role": "user", "content": data.message})
    response = await groqApi(histories)
    dataIA = await getMatchingNextQuestion(response) 
    messageIA = dataIA["messageIA"] if data else "" 

    if data:
        assistance = {"role": "assistant", "content": messageIA}
        histories.append(assistance)
        savedata.append({"role": "user", "content": data.message})
        savedata.append(assistance)
        await updateMatchingRepo(user_id, messages = savedata, score = dataIA['score'], resume = dataIA['resume'])
    return messageIA



@matching_router.get("/messages/{user_id}")
async def getAllMatchingMessages(user_id: str): 
    messages = await getInvitationsRepo(user_id)

    return messages
    return []



@matching_router.get("/search/{user_id}")
async def getMatching(user_id: str): 
    otherUsers = await getUsersWithHighScore(user_id)
    userMatchingItem = await getMatchingByUserRepo(user_id)
    usersFind = []
    if not userMatchingItem:
        return "ITEM NOT FOUND"
    elif not otherUsers:
        return "USERS NOT FOUND"
    else:
        for user in otherUsers:
            resume1 = userMatchingItem.get('resume')
            resume2 = user.get('resume')
            completPrompt = build_matching_prompt(resume1, resume2)
            response = await groqApi([{"role": "system", "content": completPrompt}])
            response = response.get("message") 
            data = json.loads(response)
            if data:
                if data["compatibility_score"] and data["compatibility_score"] > 0:
                    usersFind.append({"user" : user,  "result" : data})

    return usersFind



@matching_router.post('/invitation/{user_id}')
async def sendInvitation(user_id : str, data : MachingGuestInput):

    invitation_id = await createGuestInvitationRepo(user_id, data)

    return invitation_id



@matching_router.get('/invitations/{user_id}')
async def getMyAllInvitations(user_id : str):

    invitations = await getInvitationsRepo(user_id)

    return invitations


@matching_router.put('/invitation/{invitation_id}')
async def updateInvitation(invitation_id : str, data : UpdateMachingGuestInput):
    response = "" 
    invitation = await getMatchingInvitationRepo(invitation_id)
    if invitation: 
        if  invitation.get("guest_id") == data.guest_id: 
            response = await updateGuestInvitationRepo(invitation_id, data)
            if response != "" and data.status == "ACCEPTED" : 
                connexion_id = await createConnexionRepo(invitation_id, invitation.get("user_id"), invitation.get("guest_id"))

    return response



@matching_router.get('/connexions/{user_id}')
async def getAllUserConnexions(user_id: str ):
    connexions = await getAllUserConnexionsRepo(user_id)

    return connexions


@matching_router.get('/connexion/{user_id}')
async def getUserConnexion(user_id: str, invitation_id : str):
    invitation = await getMatchingInvitationRepo(invitation_id)
    if not invitation:
        return "INVITATION NOT FOUND"
    
    if invitation.get("guest_id") != user_id:
        return "NOT GUEST USER"
    
    connexion_id = await createConnexionRepo(invitation_id, invitation.get("user_id"), invitation.get("guest_id"))

    return connexion_id



@matching_router.post('/connexion/message/{connexion_id}')
async def connexionSendMessage(connexion_id: str, data: ConnexionMessageInput):
    connexion = await getConnexionRepo(connexion_id)
    if not connexion:
        return "CONNEXION NOT FOUND"
    
    connexion_id = await updateConnexionRepo(connexion_id, data)

    return connexion_id


@matching_router.post('/connexion/{user_id}/{invitation_id}')
async def acceptInvitationAndCreateConnexion(user_id: str, invitation_id : str):
    invitation = await getMatchingInvitationRepo(invitation_id)
    if not invitation:
        return "INVITATION NOT FOUND"
    
    if invitation.get("guest_id") != user_id:
        return "NOT GUEST USER"
    
    connexion_id = await createConnexionRepo(invitation_id, invitation.get("user_id"), invitation.get("guest_id"))

    return connexion_id


@matching_router.get("/open-matching/{user_id}")
async def openToMatch(user_id: str):
    checkExist = await db.matching.find_one({"user_id" : user_id})

    if checkExist:
        userMessages = checkExist.get("messages")
        return userMessages[2:]
    else : 
        chat_history = [{"role": "assistant", "content": await getInitPrompt(user_id) }]
        chat_history.append({"role": "user", "content": """ commence avec la première question"""}) 

        response = await groqApi(  chat_history,  ) 
        chat_history.append({"role": "assistant", "content": response.choices[0].message.content})
         
        await db.matching.insert_one({
            "user_id" : user_id,
            "messages" : chat_history,
        })

        return chat_history[2:]

@matching_router.post("/answer/{user_id}")
async def answer(user_id: str , input: ChatInput):
    conversationItem = await db.matching.find_one({"user_id" : user_id})
    chat_history = conversationItem.get("messages") if conversationItem else []

    chat_history.append({"role": "user", "content": input.message})

    response = await groqApi( chat_history ) 
    chat_history.append({"role": "assistant", "content": response.choices[0].message.content})

    await db.matching.update_one(
        {"user_id": conversationItem.get("user_id")},              # Filtre
        {"$set": {"messages": chat_history}}     # Action
    )

    return response.choices[0].message.content

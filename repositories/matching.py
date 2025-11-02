from config import DB
import uuid
from models.models import MachingInput, ConnexionMessageInput, MachingGuestInput, UpdateMachingGuestInput
from bson.son import SON
from repositories.users import getUserRepo
from datetime import datetime

IN_PROGRESS = "IN_PROGRESS"


async def getMatchingRepo(matching_id : str):
    return await DB.matching.find_one({"matching_id" : matching_id}, {"_id": 0})


async def getMatchingByUserRepo(user_id : str):
    matching = await DB.matching.find_one({"user_id" : user_id}, {"_id": 0})
    return matching
    return "" if not matching else matching.get("matching_id")


async def createMatchingRepo(user_id : str, messages = []): 
    unique_code = str(uuid.uuid4())
    user =  await getUserRepo(user_id)
    await DB.matching.insert_one({
        "matching_id" : unique_code,
        "user_id" : user_id,
        "age" : user.get("age"),
        "name" : user.get("pseudo"),
        "dateOfBirth" : user.get("dateOfBirth"),
        "country" : user.get("country"),
        "sexe" : user.get("sexe"),
        "messages" : messages,
        "score" : 0,
        "resume" : ""
        # "name" : data.name,
    })

    return unique_code


async def updateMatchingRepo(user_id : str, messages = [], score = "",resume = ""):
    await DB.matching.update_one(
            {"user_id": user_id},              # Filtre
            {"$set": {"messages": messages,"score": score, "resume" : resume} }     # Action
        )

    return user_id



async def getUsersWithHighScore(user_id, page = 1 , limit =10):

    skip = (page - 1) * limit
    total_users = await DB.matching.count_documents({}) - 1
    limit = min(limit, total_users)
     
    # SELECTIONNER LES INVITATIONS ENVOYE OU RECU PAR L'USER
    userInvitations = await DB.invitation.aggregate([{
        "$match": {
                "$or": [
                    {"user_id": user_id, },
                    {"guest_id": user_id, }
                ]
            }}]).to_list(length=None)
    
    #
    invited_user_ids = [user_id] + [
        invitation["guest_id"] 
        if invitation["guest_id"] != user_id 
        else invitation["user_id"] 
        for invitation in userInvitations
    ] 

    cursor = DB.matching.aggregate([
        {
            "$match": {
                # "user_id": {"$ne": user_id},  # différent de l'utilisateur courant
                "user_id": {"$nin": invited_user_ids}
            }
        },
        # {
        #     # conversion du score (string -> int)
        #     "$addFields": {
        #         "score_int": {"$toInt": "$score"}
        #     }
        # },
        # {
            # # filtre sur les scores supérieurs à 75
            # "$match": {
            #     "score_int": {"$gt": 0}
            # }
            # "$match": {
            #     "score": {"$gt": 0}
            # }
        # },
        {"$sample": {"size": total_users}},   # mélange tout aléatoirement
        {"$skip": skip},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "user_id": 1,
                "score": 1,
                "name": 1,
                "age" : 1,
                "sexe" : 1,
                "dateOfBirth" : 1,
                "country" : 1,
                # "score_int": 1,
                "resume": 1
            }
        }
    ])

    return await cursor.to_list(length=limit)

    return {
        "page" : page,
        "limit" : limit,
        "total" : total_users,
        "data" : users
    }

    

async def getInvitationsRepo(user_id : str):
    
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"user_id": user_id, "status" : "IN_PROGRESS" },
                    {"guest_id": user_id, "status" : "IN_PROGRESS" }
                ]
            }
        },
        {
            "$lookup": {
                "from": "users",          # nom de la collection users
                "localField": "user_id",  # champ dans la collection invitation
                "foreignField": "user_id",# champ correspondant dans users
                "as": "user_info"         # nom du champ résultant
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "guest_id",
                "foreignField": "user_id",
                "as": "guest_info"
            }
        },
        {
            "$unwind": "$user_info"   # on "détache" les sous-documents (facultatif)
        },
        {
            "$unwind": "$guest_info"
        },
        {
            "$project": {             # on choisit les champs à afficher
                "_id": 0,
                "invitation_id": 1,
                "user_id": 1,
                "guest_id": 1,
                "compatibility_score": 1,
                "guest_resume": 1,
                "reason": 1,
                "advice": 1,
                "user_info.dateOfBirth": 1,
                "user_info.pseudo": 1,
                "user_info.sexe": 1,
                "user_info.country": 1,
                "user_info.occupation": 1,
                "user_info.imageProfile":1,
                "guest_info.dateOfBirth": 1,
                "guest_info.pseudo": 1,
                "guest_info.sexe": 1,
                "guest_info.country": 1,
                "guest_info.occupation": 1,
                "guest_info.imageProfile":1,
            }
        }
    ]

    invitations = await DB.invitation.aggregate(pipeline).to_list(length=None)


    # invitations = await DB.invitation.find(
    #     {
    #         "$or": [
    #             {"user_id": user_id, "status": IN_PROGRESS},
    #             {"guest_id": user_id, "status": IN_PROGRESS}
    #         ]
    #     },
    #     {"_id": 0}
    # ).to_list(length=None)

    return invitations


async def createGuestInvitationRepo(user_id : str, data : MachingGuestInput): 
    
    invitation = await DB.invitation.find_one(
        {
            "$or": [
                {"user_id": user_id, "guest_id": data.guest_id},
                {"user_id": data.guest_id, "guest_id": user_id}
            ]
        },
        {"_id": 0}
    )

    if invitation:
        unique_code = invitation.get("invitation_id")
    else:  
        unique_code = str(uuid.uuid4())
        await DB.invitation.insert_one({
            "invitation_id" : unique_code,
            "user_id" : user_id,
            "guest_id" : data.guest_id,
            "compatibility_score" : data.compatibility_score,
            "guest_resume" : data.guest_resume,
            "reason" : data.reason,
            "advice" : data.advice,
            "status" : IN_PROGRESS,
        })

    return unique_code


async def getMatchingInvitationRepo(invitation_id : str):
    invitation = await DB.invitation.find_one({"invitation_id" : invitation_id}, {"_id": 0})
    return invitation



async def updateGuestInvitationRepo(invitation_id : str , data: UpdateMachingGuestInput):
    
    checkGuest = await DB.invitation.find_one({"invitation_id" : invitation_id, "guest_id" : data.guest_id}, {"_id": 0})
    
    if not checkGuest :
        return ""

    invitation = await DB.invitation.update_one(
            {"invitation_id": invitation_id},              # Filtre
            {"$set": {"status" : data.status} }         # Action
        )
    
    return invitation_id if invitation.matched_count > 0 else ""


async def createConnexionRepo(invitation_id : str , user_id : str, guest_id : str):
    unique_code = str(uuid.uuid4())
    await DB.connexion.insert_one({
        "connexion_id" : unique_code,
        "invitation_id" : invitation_id,
        "user_id" : user_id,
        "guest_id" : guest_id,
        "messages" : [{"user_id" : "system", "message" : "Nouvelle connexion", "date" : datetime.now().isoformat()}],
        "updated_at" : datetime.now(),
    })

    return unique_code

# requete de récupération d'une connexion
async def getConnexionRepo(connexion_id):
    
    connexion = await DB.connexion.find_one(
        {"connexion_id": connexion_id },
        {"_id": 0}
    )

    return connexion

# requete de mis d'une connexion 
# c'est la requete utilisée principalement pour ajouter un message dans la conversation entre 2 personnes
async def updateConnexionRepo(connexion_id : str, data : ConnexionMessageInput):
    connexion = await DB.connexion.find_one({"connexion_id" : connexion_id}, {"_id": 0})
    if connexion:
        messages = connexion.get("messages").copy()
        messages.append({"user_id" : data.user_id, "message" : data.message, "date" : datetime.now().isoformat()})
        await DB.connexion.update_one(
            {"connexion_id": connexion_id},              # Filtre
            {"$set": {"messages": messages, "updated_at" : datetime.now(),} }     # Action
        )

    return connexion_id
    

    
async def getAllUserConnexionsRepo(user_id : str):
    
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"user_id": user_id },
                    {"guest_id": user_id }
                ]
            }
        },
        {
            "$lookup": {
                "from": "users",          # nom de la collection users
                "localField": "user_id",  # champ dans la collection invitation
                "foreignField": "user_id",# champ correspondant dans users
                "as": "user_info"         # nom du champ résultant
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "guest_id",
                "foreignField": "user_id",
                "as": "guest_info"
            }
        },
        {
            "$unwind": "$user_info"   # on "détache" les sous-documents (facultatif)
        },
        {
            "$unwind": "$guest_info"
        },
        {
            "$project": {             # on choisit les champs à afficher
                "_id": 0,
                "connexion_id": 1,
                "invitation_id": 1,
                "messages": 1,
                "user_id": 1,
                "guest_id": 1,
                "user_info.user_id": 1,
                "user_info.name": 1,
                "user_info.age": 1,
                "user_info.pseudo": 1,
                "user_info.imageProfile": 1,
                "guest_info.user_id": 1,
                "guest_info.name": 1,
                "guest_info.age": 1,
                "guest_info.pseudo": 1,
                "guest_info.imageProfile": 1,
                "updated_at": 1   # 🔥 important : inclure le champ pour pouvoir trier dessus
            }
        },
        {
            "$sort": {
                "updated_at": -1   # 🔽 -1 = ordre décroissant (les plus récents d'abord)
            }
        }
    ]

    connexions = await DB.connexion.aggregate(pipeline).to_list(length=None)







    # connexions = await DB.connexion.find(
    #     {
    #         "$or": [
    #             {"user_id": user_id },
    #             {"guest_id": user_id }
    #         ]
    #     },
    #     {"_id": 0}
    # ).to_list(length=None)

    return connexions
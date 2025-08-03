from fastapi import APIRouter
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE
from models.models import IaModel
import openai
from typing import Literal

openia_router = APIRouter(prefix="/openia",tags=["OpenIA"] )

API_SELECT : Literal["test","summary","mail","correcteur"] = "test"

HISTORIES = {
    "test": [],
    "summary": [],
    "mail" : [],
    "correcteur": []
}

def template(text = ""):
    global API_SELECT 
    
    print(API_SELECT)

    openai.api_key = OPENAI_API_KEY 

    HISTORIES[API_SELECT].append({ "role": "user", "content": text })

    response = openai.ChatCompletion.create(
        model= MODEL_NAME,
        messages=HISTORIES[API_SELECT],
        temperature= TEMPERATURE
    )

    HISTORIES[API_SELECT].append({ "role": "assistant", "content": response.choices[0].message["content"] })

    print(HISTORIES[API_SELECT])

    return response
    

@openia_router.post("/test")
async def test(ia: IaModel):
    global API_SELECT 
    API_SELECT = "test" 
    
    return template(ia.content) 

@openia_router.post("/summary")
async def summary(ia: IaModel): 
    global API_SELECT 
    API_SELECT = "summary" 

    system = "Tu es un professeur agrégée en français qui produit d'excellent résumé de texte de façon claire et concise." 

    text = f"""{system}, rédige un résumé du texte proposer et 
                   rend le texte le plus concis possible avec au plus les 1/10 du nombre de mots utiliser dans le texte original, 
                   le texte dans le style : {ia.style}.le texte est : {ia.content}"""

    return template(text) 


@openia_router.post("/mail")
async def mail(ia: IaModel = {"content" : "", "style" : "formel"}): 
    global API_SELECT 
    API_SELECT = "mail"

    system = """Tu es un expert en rédation de mail professionnel en entreprise, tu forme aujourd'hui
        en une école prestigieuse l'art de rédation de mail professionnel, rédige un exemple
         qui prend en compte tous les points clé pour rendre un mail profession de façon 
         claire et concise.""" 

    text = f"""{system}, en te basant sur un theme ou la situation qui sera donné a la fin , 
                    avec le style : {ia.style}.le theme ou situation est : {ia.content}"""

    return template(text) 


@openia_router.post("/correcteur")
async def correcteur(ia: IaModel = {"content" : ""}): 
    global API_SELECT 
    API_SELECT = "correcteur" 

    system = """Tu es le ressponsable de l'académie français avec des compétences grammatical extraordinaire""" 

    text = f"""{system}, corrige le texte a la fin dans un premier temps tu fais juste une 
        correction du texte en l'idantifiant avec le titre corretion et par la suite tu fais 3 propositions
        de reformulation du texte corrigé en gardant le même ton et sens mais dans un style professionnel,
        sans oublié de numéroté les propositions. le texte a corrigé est : {ia.content}"""

    return template(text)
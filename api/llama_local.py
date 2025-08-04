from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage
from fastapi import APIRouter
from data.llama import system_prompt

class Question():
    prompt: str

llama_router = APIRouter(prefix="/llama",tags=["LLAMA 3"] ) 

# 1. Le modèle local
llm = OllamaLLM(model="mistral", temperature=0.7)

# 2. Le prompt structuré pour une conversation
prompt = ChatPromptTemplate.from_messages([
    #("system", "Tu es un assistant utile."),
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", "{input}")
])

# 3. Chaîne logique : prompt -> modèle
chain = prompt | llm 

# Dictionnaire global pour stocker l’historique des sessions
historique_sessions = {}

# Fonction nommée pour récupérer ou créer une mémoire
def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in historique_sessions:
        historique_sessions[session_id] = InMemoryChatMessageHistory()
    return historique_sessions[session_id]

@llama_router.post("/test")
def test(question =  ""): 

    session_id = "user-1"
    # 4. Ajouter la mémoire
    chat = RunnableWithMessageHistory(
        chain,
        get_chat_history,
        input_messages_key="input",
        history_messages_key="messages",
    )

    # 5. Dialogue avec mémoire implicite (test 1)
    reponse = chat.invoke(
        {"input": [HumanMessage(content=question)]},
        config={"configurable": {"session_id": session_id}},
    ) 
 
    return reponse
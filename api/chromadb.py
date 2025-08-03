from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from fastapi import APIRouter
from openai import BaseModel 
from data.chromadb import texts, metadatas

class Question(BaseModel):
    prompt: str

chromadb_router = APIRouter(prefix="/chromedb",tags=["Chrome DB"] ) 

embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

client = Chroma(persist_directory="./chroma_db", embedding_function=embedding)
 
client.add_texts(texts, metadatas=metadatas)

llm = ChatOllama(model="mistral")

template = """
Tu es un assistant expert. Réponds de façon claire et précise à la question suivante {question}
en t'appuyant uniquement sur le contexte fourni ci-dessous  {context} 
Réponse précise :
"""

prompt = PromptTemplate.from_template(template)

# chain = LLMChain(llm=llm, prompt=prompt)
chain = prompt | llm

@chromadb_router.post("/test")
def test(search : str):
    
    # Requête
    results = client.similarity_search(search, k=1)
    print(results[0].page_content) 
 
    return results


def get_context(question: str, k: int = 1):
    docs = chain.similarity_search(question, k=k)
    return "\n\n".join([doc.page_content for doc in docs])


@chromadb_router.post("/ask")
async def ask(question: Question):
    try:

        context = get_context(question)
        return context
        response = chain.invoke({"question": question.prompt, "context": context})
        return response.content 
        # return {"question": question.prompt, "answer": answer}
    except Exception as e:
        return {"error": str(e)}
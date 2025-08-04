from fastapi import FastAPI, Query
from typing import Union, List
from cors import setup_cors
from models.models import Item, ModelName, IaModel
from api.openia import openia_router 
# from api.chromadb import chromadb_router
from api.llama_local import llama_router 
from api.groq import groq_router


app = FastAPI() 

setup_cors(app)

app.include_router(openia_router)
# app.include_router(chromadb_router)
app.include_router(llama_router)
app.include_router(groq_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"} 

@app.get("/items/")
async def read_items(q: Union[List[str], None] = Query(default=None)):
    query_items = {"q": q}
    return query_items

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

@app.get("/users/me")
def read_user_me():
    return {"username": "me"}

@app.get("/users/{username}")
def read_user(username: str):
    return {"username": username} 

@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}

@app.get("/files/{file_path:path}")
def get_file(file_path: str):
    return {"file_path": file_path} 

@app.get("/users/{user_id}/items/{item_id}")
def get_user_item(user_id: int, item_id: str, q: str = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})   
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item



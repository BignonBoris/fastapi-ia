from pydantic import BaseModel
from enum import Enum
from typing import Union, Literal


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

    
class Item(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

class IaModel(BaseModel):
    role: Literal["assistant", "user","system"] = "user"
    content: str
    style: Literal["formel", "simple","neutre"] = "neutre"


class ChatInput(BaseModel):
    message: str


class UserInput(BaseModel):
    name: str
    age: int
    sexe: str
    country: str
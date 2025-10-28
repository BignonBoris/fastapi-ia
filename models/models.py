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
    image: str = ""
    pseudo: str = ""
    country: str = ""
    phone: str = ""
    dateOfBirth: str = ""
    sexe: str = ""
    occupation: str = ""
    email: str = ""
    password: str = ""
    name: str = ""
    age: int = 0
    fcmToken: str = ""


class MessageInput(BaseModel):
    messages: dict


class MachingInput(BaseModel):
    message : str


class MachingGuestInput(BaseModel):
    guest_id : str
    guest_resume : str = ""
    compatibility_score: int = 0
    reason : str = ""
    advice : str = ""


class UpdateMachingGuestInput(MachingGuestInput):
    status : str

class ConnexionMessageInput(BaseModel):
    user_id : str
    message : str
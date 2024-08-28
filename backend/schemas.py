from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    paswd: str
    name: str
    admin: int = 0

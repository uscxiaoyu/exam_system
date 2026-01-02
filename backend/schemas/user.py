from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: str = "teacher"

class UserUpdate(UserBase):
    password: Optional[str] = None
    role: Optional[str] = None

class UserInDBBase(UserBase):
    id: int
    role: str
    school_id: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    password_hash: str

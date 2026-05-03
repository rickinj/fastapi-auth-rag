from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class RoleCreate(BaseModel):
    name: str

class DocumentCreate(BaseModel):
    title: str
    company_name: str
    document_type: str
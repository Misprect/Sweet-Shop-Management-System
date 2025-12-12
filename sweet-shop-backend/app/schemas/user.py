from pydantic import BaseModel, Field
#Schema for user registration (Input)
class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=8)

#Schema for the JWT token response (Output)
class Token(BaseModel):
    access_token: str
    token_type: str= "bearer"
    user_role: str
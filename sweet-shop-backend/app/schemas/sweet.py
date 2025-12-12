from pydantic import BaseModel, Field
from typing import Optional

#---1.Base schema (used for common attributes)---
class SweetBase(BaseModel):
    name: str= Field(..., max_length=100)
    description: Optional[str]= Field (None, max_length=500)
    price: float= Field(..., gt=0.0)
    stock_quantity: int = Field(..., ge=0)
    is_available: bool= True
    category: str= Feild(..., max_length=50)

# --- 2. Schema for creating a new sweet(inherit base)---
class SweetCreate(SweetBase):
    pass

#--- 3. Schema for updating an existing sweeet(all fields optional)---
class SweetUpdates(SweetBase):
    name: Optional[str]= Field(None, max_length=100)
    price: Optional[float]= Field(None, gt=0.0)
    srock_quantity: Optional[int]= Field(None, ge=0)
    category: Optional[str]= Feild(None, max_length=50)

#--- 4. Schema for reading/returning a Sweet(includes DB-generated ID)---
class Sweets(SweetBase):
    id: int
    owner_id: int#we assume sweets are managed by a user/admin

    class Config:
        from_attributes= True

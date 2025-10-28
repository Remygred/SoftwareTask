
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

# Auth
class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = None

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Pets
class PetIn(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    sex: Optional[str] = None
    birth_date: Optional[date] = None
    neutered: Optional[str] = None
    weight_kg: Optional[str] = None

class PetOut(PetIn):
    id: int
    owner_id: int
    class Config: from_attributes = True

# Health
class HealthIn(BaseModel):
    type: str
    value: Optional[str] = None
    note: Optional[str] = None
    date: date

class HealthOut(HealthIn):
    id: int
    pet_id: int
    class Config: from_attributes = True

# Reminders
class ReminderIn(BaseModel):
    kind: str
    due_date: date
    title: str
    note: Optional[str] = None

class ReminderOut(ReminderIn):
    id: int
    pet_id: int
    completed: int
    class Config: from_attributes = True

# Recipes
class RecipeIn(BaseModel):
    species: str
    stage: str
    title: str
    content: str

class RecipeOut(RecipeIn):
    id: int
    class Config: from_attributes = True

# Articles
class ArticleIn(BaseModel):
    title: str
    category: str | None = None
    content: str

class ArticleOut(ArticleIn):
    id: int
    class Config: from_attributes = True

# Lost
class LostIn(BaseModel):
    pet_name: str
    species: str | None = None
    description: str | None = None
    contact: str | None = None

class LostOut(LostIn):
    id: int
    last_seen: datetime
    class Config: from_attributes = True


from sqlalchemy import Column, Integer, BigInteger, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    display_name = Column(String(255))
    role = Column(String(32), nullable=False, default="member")
    created_at = Column(DateTime, server_default=func.now())

class Pet(Base):
    __tablename__ = "pets"
    id = Column(BigInteger, primary_key=True)
    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    species = Column(String(50), nullable=False)   # dog/cat/...
    breed = Column(String(100))
    sex = Column(String(10))                       # male/female/unknown
    birth_date = Column(Date)
    neutered = Column(String(10))                  # yes/no/unknown
    weight_kg = Column(String(10))
    created_at = Column(DateTime, server_default=func.now())

class HealthRecord(Base):
    __tablename__ = "health_records"
    id = Column(BigInteger, primary_key=True)
    pet_id = Column(BigInteger, ForeignKey("pets.id"), nullable=False)
    type = Column(String(50), nullable=False)      # weight/medication/vaccine/symptom/visit
    value = Column(Text)                           # e.g., 4.2 (kg) / Amoxicillin-250mg
    note = Column(Text)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(BigInteger, primary_key=True)
    pet_id = Column(BigInteger, ForeignKey("pets.id"), nullable=False)
    kind = Column(String(50), nullable=False)      # vaccine/deworming/medication/checkup
    due_date = Column(Date, nullable=False)
    title = Column(String(255), nullable=False)
    note = Column(Text)
    completed = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(BigInteger, primary_key=True)
    species = Column(String(50), nullable=False)
    stage = Column(String(50), nullable=False)     # puppy/adult/senior
    title = Column(String(255), nullable=False)
    content = Column(Text)

class Article(Base):
    __tablename__ = "articles"
    id = Column(BigInteger, primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100))
    content = Column(Text)

class LostPost(Base):
    __tablename__ = "lost_posts"
    id = Column(BigInteger, primary_key=True)
    pet_name = Column(String(100), nullable=False)
    species = Column(String(50))
    last_seen = Column(DateTime, server_default=func.now())
    description = Column(Text)
    contact = Column(String(255))

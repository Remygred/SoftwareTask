from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base

# 说明：
# - SQLite 需要 "INTEGER PRIMARY KEY" 才会自增；因此所有 id / 外键统一用 Integer。
# - 若未来切 PostgreSQL，不受影响（Integer 也完全 OK）。

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    display_name = Column(String(255))
    role = Column(String(32), nullable=False, default="member")
    created_at = Column(DateTime, server_default=func.now())

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # ✅
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
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)  # ✅
    type = Column(String(50), nullable=False)      # weight/medication/vaccine/symptom/visit
    value = Column(Text)                           # e.g., "4.2" / "Amoxicillin-250mg"
    note = Column(Text)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)  # ✅
    kind = Column(String(50), nullable=False)      # vaccine/deworming/medication/checkup
    due_date = Column(Date, nullable=False)
    title = Column(String(255), nullable=False)
    note = Column(Text)
    completed = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    species = Column(String(50), nullable=False)
    stage = Column(String(50), nullable=False)     # puppy/adult/senior
    title = Column(String(255), nullable=False)
    content = Column(Text)

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    title = Column(String(255), nullable=False)
    category = Column(String(100))
    content = Column(Text)

class LostPost(Base):
    __tablename__ = "lost_posts"
    id = Column(Integer, primary_key=True, autoincrement=True)  # ✅
    pet_name = Column(String(100), nullable=False)
    species = Column(String(50))
    last_seen = Column(DateTime, server_default=func.now())
    description = Column(Text)
    contact = Column(String(255))

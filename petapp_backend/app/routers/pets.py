from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

@router.get("", response_model=list[schemas.PetOut])
def list_pets(db: Session = Depends(get_db)):
    return db.query(models.Pet).all()

@router.post("", response_model=schemas.PetOut, status_code=201)
def create_pet(data: schemas.PetIn, db: Session = Depends(get_db)):
    p = models.Pet(owner_id=1, **data.dict())  # TODO: 从 JWT 取真实用户
    db.add(p); db.flush()
    return p

@router.get("/{pid}", response_model=schemas.PetOut)
def get_pet(pid: int, db: Session = Depends(get_db)):
    p = db.get(models.Pet, pid)
    if not p: raise HTTPException(404, "Pet not found")
    return p

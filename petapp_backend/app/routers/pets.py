
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

def db_dep():
    from ..db import get_db as _get
    return next(_get())

@router.get("", response_model=list[schemas.PetOut])
def list_pets(db: Session = Depends(db_dep)):
    return db.query(models.Pet).all()

@router.post("", response_model=schemas.PetOut, status_code=201)
def create_pet(data: schemas.PetIn, db: Session = Depends(db_dep)):
    # 演示用：owner 固定为 1（正式版从 JWT 解析）
    p = models.Pet(owner_id=1, **data.dict())
    db.add(p); db.flush()
    return p

@router.get("/{pid}", response_model=schemas.PetOut)
def get_pet(pid: int, db: Session = Depends(db_dep)):
    p = db.get(models.Pet, pid)
    if not p: raise HTTPException(404, "Pet not found")
    return p

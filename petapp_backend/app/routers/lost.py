from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

@router.get("", response_model=list[schemas.LostOut])
def list_posts(db: Session = Depends(get_db)):
    return db.query(models.LostPost).all()

@router.post("", response_model=schemas.LostOut, status_code=201)
def create_post(data: schemas.LostIn, db: Session = Depends(get_db)):
    p = models.LostPost(**data.dict())
    db.add(p); db.flush()
    return p


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

def db_dep():
    from ..db import get_db as _get
    return next(_get())

@router.get("", response_model=list[schemas.LostOut])
def list_posts(db: Session = Depends(db_dep)):
    return db.query(models.LostPost).all()

@router.post("", response_model=schemas.LostOut, status_code=201)
def create_post(data: schemas.LostIn, db: Session = Depends(db_dep)):
    p = models.LostPost(**data.dict())
    db.add(p); db.flush()
    return p

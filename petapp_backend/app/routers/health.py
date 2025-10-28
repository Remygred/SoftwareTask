from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

@router.get("/{pet_id}/records", response_model=list[schemas.HealthOut])
def list_records(pet_id: int, db: Session = Depends(get_db)):
    return db.query(models.HealthRecord).filter(models.HealthRecord.pet_id == pet_id).all()

@router.post("/{pet_id}/records", response_model=schemas.HealthOut, status_code=201)
def create_record(pet_id: int, data: schemas.HealthIn, db: Session = Depends(get_db)):
    rec = models.HealthRecord(pet_id=pet_id, **data.dict())
    db.add(rec); db.flush()
    return rec

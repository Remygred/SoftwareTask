from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

@router.get("/{pet_id}", response_model=list[schemas.ReminderOut])
def list_reminders(pet_id: int, db: Session = Depends(get_db)):
    return db.query(models.Reminder).filter(models.Reminder.pet_id == pet_id).all()

@router.post("/{pet_id}", response_model=schemas.ReminderOut, status_code=201)
def create_reminder(pet_id: int, data: schemas.ReminderIn, db: Session = Depends(get_db)):
    r = models.Reminder(pet_id=pet_id, **data.dict())
    db.add(r); db.flush()
    return r

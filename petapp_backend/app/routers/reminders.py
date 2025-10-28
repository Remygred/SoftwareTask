
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

def db_dep():
    from ..db import get_db as _get
    return next(_get())

@router.get("/{pet_id}", response_model=list[schemas.ReminderOut])
def list_reminders(pet_id: int, db: Session = Depends(db_dep)):
    return db.query(models.Reminder).filter(models.Reminder.pet_id == pet_id).all()

@router.post("/{pet_id}", response_model=schemas.ReminderOut, status_code=201)
def create_reminder(pet_id: int, data: schemas.ReminderIn, db: Session = Depends(db_dep)):
    r = models.Reminder(pet_id=pet_id, **data.dict())
    db.add(r); db.flush()
    return r

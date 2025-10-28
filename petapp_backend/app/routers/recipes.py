from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

@router.get("", response_model=list[schemas.RecipeOut])
def list_recipes(species: str | None = None, stage: str | None = None, db: Session = Depends(get_db)):
    qs = db.query(models.Recipe)
    if species: qs = qs.filter(models.Recipe.species == species)
    if stage: qs = qs.filter(models.Recipe.stage == stage)
    return qs.all()

@router.post("", response_model=schemas.RecipeOut, status_code=201)
def create_recipe(data: schemas.RecipeIn, db: Session = Depends(get_db)):
    r = models.Recipe(**data.dict())
    db.add(r); db.flush()
    return r

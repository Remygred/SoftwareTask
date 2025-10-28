
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

def db_dep():
    from ..db import get_db as _get
    return next(_get())

@router.get("", response_model=list[schemas.RecipeOut])
def list_recipes(species: str | None = None, stage: str | None = None, db: Session = Depends(db_dep)):
    qs = db.query(models.Recipe)
    if species: qs = qs.filter(models.Recipe.species == species)
    if stage: qs = qs.filter(models.Recipe.stage == stage)
    return qs.all()

@router.post("", response_model=schemas.RecipeOut, status_code=201)
def create_recipe(data: schemas.RecipeIn, db: Session = Depends(db_dep)):
    r = models.Recipe(**data.dict())
    db.add(r); db.flush()
    return r


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models, schemas

router = APIRouter()

def db_dep():
    from ..db import get_db as _get
    return next(_get())

@router.get("", response_model=list[schemas.ArticleOut])
def list_articles(category: str | None = None, db: Session = Depends(db_dep)):
    qs = db.query(models.Article)
    if category: qs = qs.filter(models.Article.category == category)
    return qs.all()

@router.post("", response_model=schemas.ArticleOut, status_code=201)
def create_article(data: schemas.ArticleIn, db: Session = Depends(db_dep)):
    a = models.Article(**data.dict())
    db.add(a); db.flush()
    return a

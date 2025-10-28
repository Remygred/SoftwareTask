
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, pets, health, reminders, recipes, articles, lost

app = FastAPI(title="智慧宠物APP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/healthz")
def healthz():
    return {"ok": True}

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(pets.router, prefix="/api/pets", tags=["pets"])
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(recipes.router, prefix="/api/recipes", tags=["recipes"])
app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(lost.router, prefix="/api/lost", tags=["lost"])

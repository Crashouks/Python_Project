"""REST API для керування туристичними маршрутами.

Запуск:  uvicorn tourist_routes.api.main:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from tourist_routes.api import config, models
from tourist_routes.api.database import Base, SessionLocal, engine
from tourist_routes.api.routers import auth, routes
from tourist_routes.core.sample_data import create_sample_routes


def seed_demo_routes():
    """Додає демо-маршрути, якщо таблиця порожня."""
    with SessionLocal() as db:
        if db.scalar(select(func.count(models.RouteRecord.id))):
            return
        db.add_all(models.RouteRecord.from_domain(r) for r in create_sample_routes())
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_demo_routes()
    yield


app = FastAPI(
    title="Tourist Routes API",
    version="1.0.0",
    description="REST API для керування туристичними маршрутами. "
                "Читання відкрите; створення, зміна й видалення потребують JWT (`/auth/login`).",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(routes.router)


@app.get("/", tags=["root"])
def root():
    return {"message": "Tourist Routes API працює.", "docs": "/docs"}

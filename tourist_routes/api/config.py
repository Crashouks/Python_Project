import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'data' / 'api.db'}")

# У production обов'язково задайте власний SECRET_KEY через змінну середовища.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080",
    ).split(",")
    if origin.strip()
]

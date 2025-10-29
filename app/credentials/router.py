from fastapi import APIRouter, HTTPException

from app.shared.dependencies.db import PostgresRunnerDep

from .dto import PublicKeyResponse
from . import service as credentials_service

router = APIRouter()


@router.get("/public-key")
async def get_public_key(db: PostgresRunnerDep) -> PublicKeyResponse:
    """Return the server's public key for encrypting data."""
    try:
        return credentials_service.get_public_key(db=db)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to load public key")

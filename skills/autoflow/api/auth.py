# MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""JWT + API Key 双认证"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, APIKeyHeader, APIKeyQuery

from fastapi import APIRouter
from api.config import settings

router = APIRouter()

_bearer = HTTPBearer(auto_error=False)
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
_api_key_query = APIKeyQuery(name="api_key", auto_error=False)

# In-memory API key store (persisted in DB table `clients` via api/utils/db.py)
_api_keys: dict[str, dict] = {}  # key_hash -> {client_id, name, ...}


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def generate_api_key(client_name: str, client_id: str) -> str:
    raw = f"af_{secrets.token_urlsafe(32)}"
    _api_keys[hash_api_key(raw)] = {"client_id": client_id, "name": client_name}
    return raw


def create_jwt_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    from jose import jwt
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=settings.jwt.expire_hours))
    return jwt.encode({"sub": subject, "exp": expire}, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)


def verify_jwt_token(token: str) -> dict:
    from jose import jwt, JWTError
    try:
        return jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@router.post("/login")
async def login(username: str = "", password: str = ""):
    """简单登录（生产环境应对接真实用户系统）"""
    if username and password:
        token = create_jwt_token(username)
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


async def get_current_user(
    bearer: Optional[HTTPAuthorizationCredentials] = Security(_bearer),
    header_key: Optional[str] = Security(_api_key_header),
    query_key: Optional[str] = Security(_api_key_query),
) -> dict:
    """支持三种认证：Bearer JWT、X-API-Key header、api_key query"""
    # 1. JWT Bearer
    if bearer:
        return verify_jwt_token(bearer.credentials)
    # 2. API Key
    api_key = header_key or query_key
    if api_key:
        if not api_key.startswith("af_"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key format")
        h = hash_api_key(api_key)
        if h not in _api_keys:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown API key")
        return {"sub": _api_keys[h]["client_id"], "auth": "api_key"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

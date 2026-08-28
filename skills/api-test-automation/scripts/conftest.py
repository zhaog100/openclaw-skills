# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""pytest fixtures for API test automation."""
from __future__ import annotations

import json
import os
from pathlib import Path

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env.test")

BASE_URL = os.getenv("BASE_URL", "")
AUTH_TYPE = os.getenv("AUTH_TYPE", "jwt")
JWT_TOKEN = os.getenv("JWT_TOKEN", "")
BASIC_USERNAME = os.getenv("BASIC_USERNAME", "")
BASIC_PASSWORD = os.getenv("BASIC_PASSWORD", "")
TIMEOUT = int(os.getenv("TIMEOUT_SECONDS", "30"))
RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))

@pytest.fixture(scope="session")
def client() -> httpx.Client:
    """Session-scoped httpx client with default headers."""
    headers = {"Accept": "application/json"}
    if AUTH_TYPE == "jwt" and JWT_TOKEN:
        headers["Authorization"] = f"Bearer {JWT_TOKEN}"
    elif AUTH_TYPE == "basic" and BASIC_USERNAME:
        auth = (BASIC_USERNAME, BASIC_PASSWORD)
    else:
        auth = None

    return httpx.Client(base_url=BASE_URL, headers=headers, timeout=TIMEOUT, auth=auth)

@pytest.fixture
def report_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "reports"

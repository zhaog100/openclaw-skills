# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License

"""AuthManager — JWT/Token 认证管理中心

支持：
- JWT Token 登录、刷新、缓存
- Basic Auth
- API Key
- OAuth 2.0 (Client Credentials)
- 多账号体系 (accounts)
- Token 自动刷新 (access_token + refresh_token)
"""

import json
import time
import base64
import hashlib
import hmac
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


class TokenCache:
    """Token 缓存，支持过期检查和持久化"""

    def __init__(self, cache_file: str = "data/auth_cache.json"):
        self.cache_file = Path(cache_file)
        self._cache: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self.cache_file.exists():
            try:
                self._cache = json.loads(self.cache_file.read_text())
            except Exception:
                self._cache = {}

    def _save(self):
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(json.dumps(self._cache, indent=2, ensure_ascii=False))

    def get(self, account_key: str) -> Optional[dict]:
        entry = self._cache.get(account_key)
        if entry and entry.get("expires_at", 0) > time.time():
            return entry
        return None

    def set(self, account_key: str, token_data: dict):
        token_data["cached_at"] = time.time()
        self._cache[account_key] = token_data
        self._save()

    def clear(self, account_key: Optional[str] = None):
        if account_key:
            self._cache.pop(account_key, None)
        else:
            self._cache.clear()
        self._save()


class AuthManager:
    """认证管理中心"""

    def __init__(self, accounts_config: Optional[dict] = None, cache_file: str = "data/auth_cache.json"):
        self.accounts: dict[str, dict] = accounts_config or {}
        self.token_cache = TokenCache(cache_file)

    # ── 登录 ──────────────────────────────────────────────

    def login(self, account_key: str, credentials: dict) -> dict:
        """通过用户名密码获取 JWT Token"""
        account = self.accounts.get(account_key, {})
        url = account.get("login_url", "")
        if not url:
            raise ValueError(f"Account '{account_key}' has no login_url configured")

        username = credentials.get("username", account.get("username", ""))
        password = credentials.get("password", account.get("password", ""))

        import httpx
        resp = httpx.post(url, json={"username": username, "password": password}, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        access_token = data.get("access_token") or data.get("token") or data.get("accessToken")
        refresh_token = data.get("refresh_token") or data.get("refreshToken")
        expires_in = data.get("expires_in", 3600)

        token_data = {
            "type": "jwt",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "expires_at": time.time() + expires_in - 60,  # 提前1分钟过期
        }
        self.token_cache.set(account_key, token_data)
        return token_data

    # ── Token 刷新 ────────────────────────────────────────

    def refresh_token(self, account_key: str) -> dict:
        """刷新 access_token"""
        cached = self.token_cache.get(account_key)
        if not cached:
            raise ValueError(f"No token found for account '{account_key}'")

        refresh_token = cached.get("refresh_token")
        if not refresh_token:
            raise ValueError(f"Account '{account_key}' has no refresh_token")

        account = self.accounts.get(account_key, {})
        refresh_url = account.get("refresh_url", account.get("login_url", ""))

        import httpx
        resp = httpx.post(refresh_url, json={"refresh_token": refresh_token}, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        token_data = {
            "type": "jwt",
            "access_token": data.get("access_token") or data.get("token"),
            "refresh_token": data.get("refresh_token") or refresh_token,
            "expires_in": data.get("expires_in", 3600),
            "expires_at": time.time() + data.get("expires_in", 3600) - 60,
        }
        self.token_cache.set(account_key, token_data)
        return token_data

    def get_token(self, account_key: str) -> Optional[str]:
        """获取有效的 access_token（自动刷新）"""
        cached = self.token_cache.get(account_key)
        if cached and cached.get("access_token"):
            return cached["access_token"]

        # Token 过期，尝试刷新
        try:
            refreshed = self.refresh_token(account_key)
            return refreshed.get("access_token")
        except Exception:
            return None

    # ── 多账号体系 ────────────────────────────────────────

    def register_account(self, account_key: str, config: dict):
        """注册一个认证账号"""
        self.accounts[account_key] = config
        # 持久化到 config
        config_path = Path("config/accounts.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if config_path.exists():
            try:
                existing = json.loads(config_path.read_text())
            except Exception:
                existing = {}
        existing[account_key] = config
        config_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False))

    def get_account(self, account_key: str) -> Optional[dict]:
        return self.accounts.get(account_key)

    def list_accounts(self) -> list[str]:
        return list(self.accounts.keys())

    # ── 认证头生成 ────────────────────────────────────────

    def get_auth_headers(self, account_key: str, auth_type: str = "jwt") -> dict[str, str]:
        """生成请求头"""
        headers = {}

        if auth_type == "jwt":
            token = self.get_token(account_key)
            if token:
                headers["Authorization"] = f"Bearer {token}"

        elif auth_type == "basic":
            account = self.accounts.get(account_key, {})
            username = account.get("username", "")
            password = account.get("password", "")
            creds = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {creds}"

        elif auth_type == "apikey":
            account = self.accounts.get(account_key, {})
            api_key = account.get("api_key", "")
            header_name = account.get("api_key_header", "X-API-Key")
            headers[header_name] = api_key

        return headers

    # ── OAuth 2.0 ────────────────────────────────────────

    def oauth2_client_credentials(self, account_key: str) -> dict:
        """OAuth 2.0 Client Credentials Grant"""
        account = self.accounts.get(account_key, {})
        token_url = account.get("oauth_token_url", "")
        client_id = account.get("client_id", "")
        client_secret = account.get("client_secret", "")
        scope = account.get("scope", "")

        if not token_url or not client_id or not client_secret:
            raise ValueError(f"Account '{account_key}' missing OAuth config")

        import httpx
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if scope:
            data["scope"] = scope

        resp = httpx.post(token_url, data=data, timeout=30)
        resp.raise_for_status()
        token_data = resp.json()

        token_data["type"] = "oauth2"
        token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600) - 60
        self.token_cache.set(account_key, token_data)
        return token_data

    # ── JWT 解析 ─────────────────────────────────────────

    @staticmethod
    def decode_jwt_payload(token: str) -> dict:
        """解码 JWT payload（不验证签名）"""
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")
        payload = parts[1]
        # Base64url decode
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += "=" * padding
        payload = payload.replace("-", "+").replace("_", "/")
        decoded = base64.b64decode(payload)
        return json.loads(decoded)

    @staticmethod
    def jwt_has_role(token: str, role: str) -> bool:
        """检查 JWT 是否包含指定角色"""
        payload = AuthManager.decode_jwt_payload(token)
        roles = payload.get("roles") or payload.get("role") or []
        if isinstance(roles, str):
            roles = [roles]
        return role in roles

    # ── 清理 ──────────────────────────────────────────────

    def clear_cache(self, account_key: Optional[str] = None):
        self.token_cache.clear(account_key)

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple


STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
AUTH_DIR = os.path.join(STORAGE_DIR, "auth")
USERS_FILE = os.path.join(AUTH_DIR, "users.json")
SESSIONS_FILE = os.path.join(AUTH_DIR, "sessions.json")


def _ensure_auth_store() -> None:
    os.makedirs(AUTH_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _read_json(path: str):
    _ensure_auth_store()
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _write_json(path: str, payload) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _secret_key() -> str:
    return os.getenv("AUTH_SECRET", "change-this-auth-secret-in-production")


def _hash_token(token: str) -> str:
    return hmac.new(_secret_key().encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()


def _hash_password(password: str, salt: bytes) -> str:
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return base64.b64encode(derived).decode("utf-8")


def hash_password_for_store(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = _hash_password(password, salt)
    return f"{base64.b64encode(salt).decode('utf-8')}:{digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_b64, digest = encoded.split(":")
        salt = base64.b64decode(salt_b64.encode("utf-8"))
    except ValueError:
        return False
    candidate = _hash_password(password, salt)
    return hmac.compare_digest(candidate, digest)


def create_user(username: str, password: str) -> Tuple[bool, str]:
    users = _read_json(USERS_FILE)
    if any(u.get("username", "").lower() == username.lower() for u in users):
        return False, "Username already exists."

    users.append(
        {
            "id": secrets.token_hex(12),
            "username": username,
            "password_hash": hash_password_for_store(password),
            "created_at": _utc_now().isoformat(),
        }
    )
    _write_json(USERS_FILE, users)
    return True, "User created."


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    users = _read_json(USERS_FILE)
    user = next((u for u in users if u.get("username", "").lower() == username.lower()), None)
    if not user:
        return None
    if not verify_password(password, user.get("password_hash", "")):
        return None
    return user


def create_session(user_id: str, username: str, hours_valid: int = 24) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = _hash_token(token)
    expires_at = (_utc_now() + timedelta(hours=hours_valid)).isoformat()

    sessions = _read_json(SESSIONS_FILE)
    sessions.append(
        {
            "token_hash": token_hash,
            "user_id": user_id,
            "username": username,
            "created_at": _utc_now().isoformat(),
            "expires_at": expires_at,
        }
    )
    _write_json(SESSIONS_FILE, sessions)
    return token


def get_session(token: str) -> Optional[Dict]:
    token_hash = _hash_token(token)
    sessions = _read_json(SESSIONS_FILE)
    now = _utc_now()

    valid_sessions = []
    found = None
    for session in sessions:
        try:
            exp = datetime.fromisoformat(session.get("expires_at"))
        except Exception:
            continue
        if exp <= now:
            continue
        valid_sessions.append(session)
        if session.get("token_hash") == token_hash:
            found = session

    if len(valid_sessions) != len(sessions):
        _write_json(SESSIONS_FILE, valid_sessions)
    return found


def revoke_session(token: str) -> None:
    token_hash = _hash_token(token)
    sessions = _read_json(SESSIONS_FILE)
    filtered = [s for s in sessions if s.get("token_hash") != token_hash]
    _write_json(SESSIONS_FILE, filtered)

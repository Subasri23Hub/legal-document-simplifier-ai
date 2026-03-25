import json
import os
import hashlib
import secrets
import re
from datetime import datetime

USERS_FILE = "users.json"
CHAT_HISTORY_DIR = "chat_histories"

# ── Ensure storage dirs exist ────────────────────────────────────────────────
def _ensure_dirs():
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)


# ── Password hashing (SHA-256 + salt) ────────────────────────────────────────
def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return hashed, salt


# ── Load / save users.json ───────────────────────────────────────────────────
def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ── Validation helpers ───────────────────────────────────────────────────────
def validate_username(username: str) -> str | None:
    """Returns error string or None if valid."""
    if len(username) < 3:
        return "Username must be at least 3 characters."
    if len(username) > 30:
        return "Username must be under 30 characters."
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return "Username can only contain letters, numbers, and underscores."
    return None


def validate_password(password: str) -> str | None:
    """Returns error string or None if valid."""
    if len(password) < 6:
        return "Password must be at least 6 characters."
    if len(password) > 64:
        return "Password must be under 64 characters."
    return None


# ── Core auth functions ───────────────────────────────────────────────────────
def register_user(username: str, password: str, full_name: str = "") -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str)
    """
    _ensure_dirs()
    username = username.strip().lower()

    err = validate_username(username)
    if err:
        return False, err

    err = validate_password(password)
    if err:
        return False, err

    users = _load_users()
    if username in users:
        return False, "Username already exists. Please choose another."

    hashed, salt = _hash_password(password)
    users[username] = {
        "full_name": full_name.strip(),
        "password_hash": hashed,
        "salt": salt,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
    }
    _save_users(users)
    return True, f"Account created successfully! Welcome, {full_name or username}."


def login_user(username: str, password: str) -> tuple[bool, str, dict]:
    """
    Authenticate a user.
    Returns (success: bool, message: str, user_data: dict)
    """
    _ensure_dirs()
    username = username.strip().lower()
    users = _load_users()

    if username not in users:
        return False, "Invalid username or password.", {}

    user = users[username]
    hashed, _ = _hash_password(password, user["salt"])

    if hashed != user["password_hash"]:
        return False, "Invalid username or password.", {}

    # Update last login
    users[username]["last_login"] = datetime.now().isoformat()
    _save_users(users)

    return True, f"Welcome back, {user['full_name'] or username}!", {
        "username": username,
        "full_name": user["full_name"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }


# ── Per-user chat history ─────────────────────────────────────────────────────
def _user_history_path(username: str) -> str:
    _ensure_dirs()
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", username)
    return os.path.join(CHAT_HISTORY_DIR, f"{safe_name}.json")


def load_chat_history(username: str) -> list[dict]:
    """Load this user's chat history from disk."""
    path = _user_history_path(username)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def save_chat_history(username: str, history: list[dict]):
    """Persist this user's chat history to disk."""
    path = _user_history_path(username)
    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def clear_chat_history(username: str):
    """Delete this user's chat history."""
    path = _user_history_path(username)
    if os.path.exists(path):
        os.remove(path)

import os
import platform
import getpass
import uuid
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional, Union


def normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path.strip())))


def is_windows_path(path: str) -> bool:
    return platform.system() == "Windows" or ("\\" in path and ":" in path)


def generate_artifact_id(source: str, path: Optional[str] = None, extra: Optional[str] = None) -> str:
    token = f"{source}::{path or ''}::{extra or uuid.uuid4().hex}"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_current_utc_timestamp(compact: bool = False, with_millis: bool = False) -> str:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    if compact:
        return now.strftime("%Y%m%dT%H%M%SZ")
    if with_millis:
        return now.isoformat(timespec="milliseconds")
    return now.isoformat()


def safe_load_json_file(file_path: str, default: Any = None) -> Any:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def safe_save_json_file(file_path: str, data: Union[dict, list], indent: int = 2) -> bool:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception:
        return False


def get_current_user() -> str:
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def get_system_platform() -> str:
    try:
        return platform.system()
    except Exception:
        return "unknown"


def is_valid_file(path: str) -> bool:
    try:
        return os.path.isfile(path) and os.access(path, os.R_OK)
    except Exception:
        return False


def get_file_sha256(file_path: str, chunk_size: int = 65536) -> str:
    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(chunk_size), b""):
                sha256.update(block)
        return sha256.hexdigest()
    except Exception:
        return "error"


def generate_session_uid() -> str:
    return uuid.uuid4().hex

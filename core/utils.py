import os
import platform
import getpass
import uuid
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional


def normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def is_windows_path(path: str) -> bool:
    return "\\" in path or platform.system() == "Windows"


def generate_artifact_id(source: str, path: Optional[str] = None) -> str:
    base = f"{source}-{path or uuid.uuid4().hex}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def get_current_utc_timestamp() -> str:
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()


def safe_load_json_file(file_path: str, default: Any = None) -> Any:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


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

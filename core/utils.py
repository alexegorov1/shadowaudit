import os
import platform
import getpass
import uuid
import hashlib
import json
import socket
import shutil
from datetime import datetime, timezone
from typing import Any, Optional, Union


def normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(str(path).strip())))


def is_windows_path(path: str) -> bool:
    return platform.system() == "Windows" or ("\\" in path and ":" in path)

def get_current_utc_timestamp(compact: bool = False, with_millis: bool = False) -> str:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    if compact:
        return now.strftime("%Y%m%dT%H%M%SZ")
    if with_millis:
        return now.isoformat(timespec="milliseconds")
    return now.isoformat()


def get_iso_timestamp_from_epoch(epoch: float, with_millis: bool = False) -> str:
    try:
        dt = datetime.fromtimestamp(epoch, tz=timezone.utc)
        return dt.isoformat(timespec="milliseconds" if with_millis else "seconds")
    except Exception:
        return "1970-01-01T00:00:00Z"


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


def get_hostname(fqdn: bool = False) -> str:
    try:
        return socket.getfqdn() if fqdn else socket.gethostname()
    except Exception:
        return "unknown"


def get_temp_dir() -> str:
    return os.environ.get("TEMP") or os.environ.get("TMP") or "/tmp"


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


def is_valid_file(path: str) -> bool:
    try:
        return os.path.isfile(path) and os.access(path, os.R_OK)
    except Exception:
        return False


def is_valid_directory(path: str) -> bool:
    try:
        return os.path.isdir(path) and os.access(path, os.X_OK)
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


def ensure_directory_exists(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception:
        return False


def get_disk_usage_percent(path: str = "/") -> float:
    try:
        total, used, free = shutil.disk_usage(path)
        return round((used / total) * 100, 2)
    except Exception:
        return 0.0


def get_system_uptime() -> float:
    try:
        if platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes
            GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
            GetTickCount64.restype = ctypes.c_ulonglong
            return round(GetTickCount64() / 1000.0, 2)
        else:
            with open("/proc/uptime", "r") as f:
                return float(f.readline().split()[0])
    except Exception:
        return 0.0


def generate_session_uid() -> str:
    return uuid.uuid4().hex

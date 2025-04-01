import os
import socket
import hashlib
import getpass
import platform
import glob
import pefile
import psutil
from datetime import datetime, timezone
from core.interfaces import BaseCollector
from core.config_loader import ConfigLoader

class FilesystemCollector(BaseCollector):
    def get_name(self) -> str:
        return "filesystem"

    def collect(self) -> list[dict]:
        hostname = socket.gethostname()
        current_user = getpass.getuser()
        system_platform = platform.system()
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        config = ConfigLoader().get("collector", {})
        fs_config = config.get("filesystem", {})
        include_dirs = fs_config.get("include_dirs", [])

        if not include_dirs:
            include_dirs = self._get_default_paths(system_platform)

        resolved_paths = []
        for pattern in include_dirs:
            expanded = glob.glob(os.path.expandvars(pattern), recursive=True)
            resolved_paths.extend(expanded)

        artifacts = []

        for path in resolved_paths:
            if not os.path.isfile(path):
                continue

            try:
                file_size = os.path.getsize(path)
                sha256_hash = self._hash_file(path)
                created_time = datetime.fromtimestamp(
                    os.path.getctime(path), tz=timezone.utc
                ).isoformat()
                is_pe = self._is_pe_file(path) if system_platform == "Windows" else False
                is_signed = False  # Placeholder

                artifact = {
                    "host_id": hostname,
                    "source": "filesystem",
                    "collected_at": current_time,
                    "artifact_type": "file_scan",
                    "confidence": 0.8,
                    "evidence_type": "execution",
                    "file_path": path,
                    "size": file_size,
                    "sha256": sha256_hash,
                    "is_pe": is_pe,
                    "is_signed": is_signed,
                    "user": current_user,
                    "platform": system_platform,
                    "created_time": created_time
                }

                artifacts.append(artifact)

            except Exception:
                continue

        return artifacts

    def _hash_file(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for block in iter(lambda: f.read(65536), b""):
                sha256.update(block)
        return sha256.hexdigest()

    def _is_pe_file(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as f:
                if f.read(2) != b"MZ":
                    return False
            pefile.PE(file_path, fast_load=True)
            return True
        except Exception:
            return False

    def _get_default_paths(self, system_platform: str) -> list[str]:
        paths = []
        if system_platform == "Windows":
            user_dirs = glob.glob("C:\\Users\\*")
            subdirs = [
                "AppData\\Local\\Temp",
                "Downloads",
                "Pictures"
            ]
            for user_dir in user_dirs:
                for subdir in subdirs:
                    path = os.path.join(user_dir, subdir)
                    paths.append(os.path.join(path, "**"))
        elif system_platform == "Linux":
            home = os.environ.get("HOME", "/home")
            paths = [
                "/tmp/**",
                os.path.join(home, "Downloads", "**"),
                os.path.join(home, "Pictures", "**")
            ]
        return paths

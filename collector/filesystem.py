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

class FilesystemCollector(BaseCollector):
    def get_name(self) -> str:
        return "filesystem"

    def collect(self) -> list[dict]:
        hostname = socket.gethostname()
        current_user = getpass.getuser()
        system_platform = platform.system()
        current_time = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        artifacts = []

        if system_platform != "Windows":
            return []

        user_dirs = glob.glob("C:\\Users\\*")
        target_subdirs = [
            "AppData\\Local\\Temp",
            "Downloads",
            "Pictures"
        ]

        target_paths = []
        for user_dir in user_dirs:
            for subdir in target_subdirs:
                full_path = os.path.join(user_dir, subdir)
                if os.path.exists(full_path):
                    target_paths.extend(
                        glob.glob(os.path.join(full_path, "**"), recursive=True)
                    )

        for path in target_paths:
            if not os.path.isfile(path):
                continue

            try:
                file_size = os.path.getsize(path)
                sha256_hash = self._hash_file(path)
                created_time = datetime.fromtimestamp(os.path.getctime(path), tz=timezone.utc).isoformat()
                is_pe = self._is_pe_file(path)
                is_signed = False  # Placeholder for future implementation

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
                dos_header = f.read(2)
                if dos_header != b"MZ":
                    return False
            pe = pefile.PE(file_path, fast_load=True)
            return True
        except Exception:
            return False

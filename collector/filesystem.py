import os
import socket
import hashlib
import getpass
import platform
import glob
import pefile
import psutil
import subprocess
from datetime import datetime, timezone
from core.interfaces import BaseCollector
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory

class FilesystemCollector(BaseCollector):
    def __init__(self):
        self.collector_config = ConfigLoader().get("collector", {})
        self.general_config = ConfigLoader().get("general", {})
        self.logger = LoggerFactory(self.general_config).create_logger("shadowaudit.collector.filesystem")
        self.system_platform = platform.system()

    def get_name(self) -> str:
        return "filesystem"

    def collect(self) -> list[dict]:
        hostname = socket.gethostname()
        current_user = getpass.getuser()
        collected_at = datetime.utcnow().replace(tz=timezone.utc).isoformat()

        fs_config = self.collector_config.get("filesystem", {})
        include_dirs = fs_config.get("include_dirs", [])
        sigcheck_path = fs_config.get("sigcheck_path", "sigcheck.exe")

        if not include_dirs:
            include_dirs = self._get_default_paths()

        resolved_paths = []
        for pattern in include_dirs:
            try:
                expanded = glob.glob(os.path.expandvars(pattern), recursive=True)
                resolved_paths.extend(expanded)
            except Exception as e:
                self.logger.warning(f"Failed to expand path pattern '{pattern}': {e}")

        artifacts = []

        for path in resolved_paths:
            if not os.path.isfile(path):
                continue

            try:
                abs_path = os.path.abspath(path)
                stat = os.stat(abs_path)
                file_size = stat.st_size
                created_time = datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat()
                sha256_hash = self._hash_file(abs_path)
                is_pe = self._is_pe_file(abs_path) if self.system_platform == "Windows" else False
                is_signed = self._is_signed_file(abs_path, sigcheck_path) if self.system_platform == "Windows" and is_pe else False

                artifact = {
                    "host_id": hostname,
                    "source": "filesystem",
                    "collected_at": collected_at,
                    "artifact_type": "file_scan",
                    "confidence": 0.8,
                    "evidence_type": "execution",
                    "file_path": abs_path,
                    "size": file_size,
                    "sha256": sha256_hash,
                    "is_pe": is_pe,
                    "is_signed": is_signed,
                    "created_time": created_time,
                    "user": current_user,
                    "platform": self.system_platform
                }

                artifacts.append(artifact)

            except Exception as e:
                self.logger.warning(f"Failed to process file '{path}': {e}")

        self.logger.info(f"Filesystem collector completed: {len(artifacts)} artifacts generated.")
        return artifacts

    def _hash_file(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for block in iter(lambda: f.read(65536), b""):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to hash file '{file_path}': {e}")
            return "error"

    def _is_pe_file(self, file_path: str) -> bool:
        try:
            with open(file_path, "rb") as f:
                if f.read(2) != b"MZ":
                    return False
            pefile.PE(file_path, fast_load=True)
            return True
        except Exception:
            return False

    def _is_signed_file(self, file_path: str, sigcheck_path: str) -> bool:
        try:
            if not os.path.isfile(sigcheck_path):
                self.logger.debug("sigcheck.exe not found or not configured.")
                return False

            result = subprocess.run(
                [sigcheck_path, "-q", "-n", "-c", file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip().lower()
            return "signed" in output
        except Exception as e:
            self.logger.debug(f"Sigcheck failed for '{file_path}': {e}")
            return False

    def _get_default_paths(self) -> list[str]:
        paths = []
        if self.system_platform == "Windows":
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
        elif self.system_platform == "Linux":
            home = os.environ.get("HOME", "/home")
            paths = [
                "/tmp/**",
                os.path.join(home, "Downloads", "**"),
                os.path.join(home, "Pictures", "**")
            ]
        return paths

import os
import socket
import hashlib
import getpass
import platform
import glob
import stat
import subprocess
from datetime import datetime, timezone
from core.interfaces import BaseCollector
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from core.pe_inspector import is_pe_file

MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

class FilesystemCollector(BaseCollector):
    def __init__(self):
        self.collector_config = ConfigLoader().get("collector", {})
        self.general_config = ConfigLoader().get("general", {})
        self.logger = LoggerFactory(self.general_config).create_logger("shadowaudit.collector.filesystem")
        self.system_platform = platform.system()
        self.sigcheck_path = "sigcheck.exe"  # Adjust if needed

    def get_name(self) -> str:
        return "filesystem"

    def collect(self) -> list[dict]:
        hostname = socket.gethostname()
        current_user = getpass.getuser()
        collected_at = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

        include_dirs = self._get_default_paths()
        resolved_paths = []

        self.logger.debug("Starting path resolution")
        for pattern in include_dirs:
            try:
                expanded = glob.glob(os.path.expandvars(pattern), recursive=True)
                resolved_paths.extend(expanded)
                self.logger.debug(f"Resolved {len(expanded)} paths from pattern: {pattern}")
            except Exception as e:
                self.logger.warning(f"Failed to expand path pattern '{pattern}': {e}")

        artifacts = []
        total_files = 0
        pe_count = 0
        signed_count = 0

        self.logger.debug("Beginning file processing loop")
        for path in resolved_paths:
            try:
                if not os.path.isfile(path):
                    continue
                if os.path.islink(path):
                    self.logger.debug(f"Skipped symlink: {path}")
                    continue
                if stat.S_ISSOCK(os.stat(path, follow_symlinks=False).st_mode):
                    self.logger.debug(f"Skipped socket: {path}")
                    continue

                abs_path = os.path.abspath(path)
                stat_info = os.stat(abs_path)
                file_size = stat_info.st_size
                if file_size > MAX_FILE_SIZE_BYTES:
                    self.logger.debug(f"Skipped large file (>100MB): {abs_path}")
                    continue

                total_files += 1
                created_time = datetime.fromtimestamp(stat_info.st_ctime, tz=timezone.utc).isoformat()

                self.logger.debug(f"Hashing file: {abs_path}")
                sha256_hash = self._hash_file(abs_path)

                is_pe = False
                is_signed = False

                if self.system_platform == "Windows":
                    self.logger.debug(f"Checking PE structure for: {abs_path}")
                    is_pe = is_pe_file(abs_path)
                    if is_pe:
                        pe_count += 1
                        self.logger.debug(f"Checking signature for PE file: {abs_path}")
                        is_signed = self._check_signature(abs_path)
                        if is_signed:
                            signed_count += 1

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

        self.logger.info(f"Filesystem collector completed: total={total_files}, artifacts={len(artifacts)}, PE={pe_count}, signed={signed_count}")
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

    def _check_signature(self, file_path: str) -> bool:
        try:
            if not os.path.isfile(self.sigcheck_path):
                self.logger.debug("sigcheck.exe not found; skipping signature check.")
                return False

            result = subprocess.run(
                [self.sigcheck_path, "-q", "-n", "-c", file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip().lower()
            return "signed" in output
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Signature check timed out for '{file_path}'")
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

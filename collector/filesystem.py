import os
import stat
import glob
import socket
import hashlib
import getpass
import platform
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
        self.sigcheck_path = self.collector_config.get("filesystem", {}).get("sigcheck_path", "sigcheck.exe")

    def get_name(self) -> str:
        return "filesystem"

    def collect(self) -> list[dict]:
        hostname = socket.gethostname()
        current_user = getpass.getuser()
        collected_at = datetime.utcnow().replace(tz=timezone.utc).isoformat()

        include_dirs = self._get_default_paths()
        resolved_paths = self._expand_globs(include_dirs)

        artifacts = []
        total_files, pe_count, signed_count = 0, 0, 0

        for path in resolved_paths:
            if not self._is_valid_file(path):
                continue

            try:
                abs_path = os.path.abspath(path)
                stat_info = os.stat(abs_path)
                file_size = stat_info.st_size
                if file_size > MAX_FILE_SIZE_BYTES:
                    self.logger.debug(f"Skipped large file: {abs_path}")
                    continue

                total_files += 1
                created_time = datetime.fromtimestamp(stat_info.st_ctime, tz=timezone.utc).isoformat()
                sha256_hash = self._hash_file(abs_path)

                is_pe = False
                is_signed = False

                if self.system_platform == "Windows":
                    is_pe = is_pe_file(abs_path)
                    if is_pe:
                        pe_count += 1
                        is_signed = self._check_signature(abs_path)
                        if is_signed:
                            signed_count += 1

                artifacts.append({
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
                })

            except Exception as e:
                self.logger.warning(f"Failed to process file: {path} — {e}")

        self.logger.info(f"Filesystem collector completed — total_files={total_files}, artifacts={len(artifacts)}, PE={pe_count}, signed={signed_count}")
        return artifacts

    def _expand_globs(self, patterns: list[str]) -> list[str]:
        resolved = []
        for pattern in patterns:
            try:
                expanded = glob.glob(os.path.expandvars(pattern), recursive=True)
                resolved.extend(expanded)
                self.logger.debug(f"Expanded pattern '{pattern}' to {len(expanded)} paths")
            except Exception as e:
                self.logger.warning(f"Glob expansion failed: {pattern} — {e}")
        return resolved

    def _is_valid_file(self, path: str) -> bool:
        try:
            if not os.path.isfile(path):
                return False
            if os.path.islink(path):
                self.logger.debug(f"Skipped symlink: {path}")
                return False
            if stat.S_ISSOCK(os.stat(path, follow_symlinks=False).st_mode):
                self.logger.debug(f"Skipped socket: {path}")
                return False
            return True
        except Exception as e:
            self.logger.debug(f"Failed file check: {path} — {e}")
            return False

    def _hash_file(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for block in iter(lambda: f.read(65536), b""):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            self.logger.warning(f"Hashing failed: {file_path} — {e}")
            return "error"

    def _check_signature(self, file_path: str) -> bool:
        if not os.path.isfile(self.sigcheck_path):
            self.logger.debug("sigcheck.exe not available")
            return False

        try:
            result = subprocess.run(
                [self.sigcheck_path, "-q", "-n", "-c", file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            output = result.stdout.strip().lower()
            return "signed" in output
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Sigcheck timeout: {file_path}")
        except Exception as e:
            self.logger.debug(f"Sigcheck failed: {file_path} — {e}")
        return False

    def _get_default_paths(self) -> list[str]:
        paths = []
        if self.system_platform == "Windows":
            user_dirs = glob.glob("C:\\Users\\*")
            for user_dir in user_dirs:
                for subdir in ["AppData\\Local\\Temp", "Downloads", "Pictures"]:
                    paths.append(os.path.join(user_dir, subdir, "**"))
        elif self.system_platform == "Linux":
            home = os.environ.get("HOME", "/home")
            paths = [
                "/tmp/**",
                os.path.join(home, "Downloads", "**"),
                os.path.join(home, "Pictures", "**")
            ]
        return paths

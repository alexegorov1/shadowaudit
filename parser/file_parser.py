import os
import re
import copy
from typing import List, Dict, Any
from parser.base_parser import BaseParser

SUSPICIOUS_EXTENSIONS = {".scr", ".vbs", ".bat", ".ps1", ".pif", ".cmd"}
PE_EXTENSIONS = {".exe", ".dll", ".sys", ".drv", ".cpl"}
MIN_PE_SIZE = 4096
SHA256_RE = re.compile(r"^[a-fA-F0-9]{64}$")

class FileParser(BaseParser):
    def get_name(self) -> str:
        return "file_parser"

        path = artifact.get("file_path", "")
        sha256 = artifact.get("sha256", "")
        size = artifact.get("size", 0)
        is_pe = artifact.get("is_pe", False)
        created = artifact.get("created_time", "")

        norm_path = os.path.normpath(path)
        artifact["file_path"] = norm_path
        artifact["directory"], artifact["filename"] = os.path.split(norm_path)
        _, ext = os.path.splitext(norm_path)
        artifact["extension"] = ext.lower()

        if ext.lower() in SUSPICIOUS_EXTENSIONS:
            tags.append("suspicious_extension")

        if ext.lower() in PE_EXTENSIONS and not is_pe:
            tags.append("pe_mismatch")

        if SHA256_RE.fullmatch(sha256) is None:
            tags.append("invalid_sha256")

        try:
            ts = created[:19]
            file_dt = datetime.fromisoformat(ts)
            age = (datetime.utcnow() - file_dt).total_seconds()
            if age < 180:
                tags.append("recent")
        except Exception:
            self.logger.debug(f"[{self._name}] Invalid timestamp format: {created}")

        if tags:
            artifact["tags"] = tags

        return artifact

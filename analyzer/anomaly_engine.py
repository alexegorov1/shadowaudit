from typing import List, Dict, Any
from analyzer.base_analyzer import BaseAnalyzer
import math
import datetime
import socket
import os
import re

class AnomalyAnalyzer(BaseAnalyzer):
    def __init__(self):
        super().__init__()
        self.name = "anomaly_analyzer"
        self.set_severity_map({
            "low_confidence": 2,
            "timestamp_drift": 3,
            "host_mismatch": 4,
            "huge_file": 5,
            "missing_required": 3,
            "suspicious_filename": 3,
            "user_mismatch": 4,
            "bad_extension": 2,
            "unsigned_pe": 4,
            "anomalous_temp_path": 3
        })
        self.system_hostname = socket.gethostname().lower()
        self.system_user = os.getenv("USERNAME") or os.getenv("USER") or "unknown"
        self.bad_ext = {".scr", ".pif", ".cpl", ".js", ".vbs", ".hta", ".jar", ".ps1", ".bat", ".cmd", ".exe"}
        self.temp_patterns = [r"\\temp\\", r"/tmp/"]

    def get_name(self) -> str:
        return self.name

    def supported_types(self) -> List[str]:
        return ["*"]

    def analyze(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for artifact in artifacts:
            matched = []
            if self._low_confidence(artifact):
                matched.append("low_confidence")
            if self._time_drift_detected(artifact):
                matched.append("timestamp_drift")
            if self._host_mismatch(artifact):
                matched.append("host_mismatch")
            if self._user_mismatch(artifact):
                matched.append("user_mismatch")
            if self._huge_file(artifact):
                matched.append("huge_file")
            if self._missing_fields(artifact):
                matched.append("missing_required")
            if self._bad_extension(artifact):
                matched.append("bad_extension")
            if self._unsigned_pe(artifact):
                matched.append("unsigned_pe")
            if self._temp_path_indicator(artifact):
                matched.append("anomalous_temp_path")
            if self._suspicious_filename(artifact):
                matched.append("suspicious_filename")
            if matched:
                severity = max(self.get_severity_for_rule(r) for r in matched)
                result = self.enrich_result(artifact, matched, severity)
                results.append(result)
            else:
                results.append(artifact)
        return results

    def _low_confidence(self, artifact: Dict[str, Any]) -> bool:
        v = artifact.get("confidence")
        return isinstance(v, (int, float)) and v < 0.3

    def _time_drift_detected(self, artifact: Dict[str, Any]) -> bool:
        try:
            collected = artifact.get("collected_at")
            if not collected:
                return False
            dt = datetime.datetime.fromisoformat(collected.replace("Z", "+00:00"))
            now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
            return abs((now - dt).total_seconds()) > 86400
        except Exception:
            return False

    def _host_mismatch(self, artifact: Dict[str, Any]) -> bool:
        actual = artifact.get("host_id", "").lower()
        return self.system_hostname and actual and self.system_hostname != actual

    def _user_mismatch(self, artifact: Dict[str, Any]) -> bool:
        reported = artifact.get("user", "").lower()
        return self.system_user and reported and reported != self.system_user

    def _huge_file(self, artifact: Dict[str, Any]) -> bool:
        size = artifact.get("size")
        return isinstance(size, int) and size > 2 * 1024 * 1024 * 1024

    def _missing_fields(self, artifact: Dict[str, Any]) -> bool:
        required = ["host_id", "artifact_type", "collected_at", "confidence", "evidence_type", "source"]
        return any(field not in artifact for field in required)

    def _bad_extension(self, artifact: Dict[str, Any]) -> bool:
        path = artifact.get("file_path", "").lower()
        _, ext = os.path.splitext(path)
        return ext in self.bad_ext

    def _unsigned_pe(self, artifact: Dict[str, Any]) -> bool:
        if not artifact.get("is_pe"):
            return False
        return artifact.get("is_signed") is False

    def _temp_path_indicator(self, artifact: Dict[str, Any]) -> bool:
        path = artifact.get("file_path", "").lower()
        return any(re.search(p, path) for p in self.temp_patterns)

    def _suspicious_filename(self, artifact: Dict[str, Any]) -> bool:
        name = os.path.basename(artifact.get("file_path", "")).lower()
        patterns = ["copy", "new", "temp", "~", "._", "_.", "1.", "2."]
        return any(p in name for p in patterns)

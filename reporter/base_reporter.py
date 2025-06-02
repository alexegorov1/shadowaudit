from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import logging
import os
import datetime
import json
import hashlib
import uuid

class BaseReporter(ABC):
    def __init__(self, output_dir: Optional[str] = "results", filename_prefix: Optional[str] = None):
        self.logger = self.get_logger()
        self.output_dir = output_dir or "results"
        self.filename_prefix = filename_prefix or self.get_name()
        os.makedirs(self.output_dir, exist_ok=True)

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def generate(self, artifacts: List[Dict[str, Any]]) -> None:
        pass

    def summarize(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Union[int, float]]:
        summary = {
            "total": len(artifacts),
            "with_analysis": 0,
            "high_severity": 0,
            "low_confidence": 0,
            "has_matched_rules": 0,
            "average_confidence": 0.0,
            "max_severity": 0,
            "distinct_hosts": set()
        }
        total_conf = 0.0
        for art in artifacts:
            summary["distinct_hosts"].add(art.get("host_id", "unknown"))
            conf = art.get("confidence")
            if isinstance(conf, (int, float)):
                total_conf += conf
                if conf < 0.3:
                    summary["low_confidence"] += 1
            if "analysis" in art:
                summary["with_analysis"] += 1
                severity = art["analysis"].get("severity", 0)
                if art["analysis"].get("matched_rules"):
                    summary["has_matched_rules"] += 1
                if severity > summary["max_severity"]:
                    summary["max_severity"] = severity
        count = summary["total"]
        summary["average_confidence"] = round(total_conf / count, 4) if count else 0.0
        summary["distinct_hosts"] = len(summary["distinct_hosts"])
        return summary

    def write_json_file(self, data: Any, filename_prefix: Optional[str] = None) -> str:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        digest = uuid.uuid4().hex[:6]
        prefix = filename_prefix or self.filename_prefix or "report"
        filename = f"{prefix}_{timestamp}_{digest}.json"
        full_path = os.path.join(self.output_dir, filename)
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.logger.info(f"{self.get_name()} wrote file: {full_path}")
        return full_path

    def group_by_type(self, artifacts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        groups = {}
        for art in artifacts:
            t = art.get("artifact_type", "unknown")
            groups.setdefault(t, []).append(art)
        return groups

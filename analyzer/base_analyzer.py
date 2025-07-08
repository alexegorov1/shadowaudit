from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
import logging
import copy

class BaseAnalyzer(ABC):
    def __init__(self):
        self.logger = self.get_logger()
        self._severity_map: Dict[str, int] = {}

    @abstractmethod
    def get_name(self) -> str:
        pass

    def should_analyze(self, artifact: Dict[str, Any]) -> bool:
        artifact_type = artifact.get("artifact_type", "").lower()
        return "*" in self.supported_types() or artifact_type in self.supported_types()

    def process_all(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = []
        for idx, art in enumerate(artifacts):
            if not self.should_analyze(art):
                continue
            try:
                analyzed = self.analyze_one(art)
                if isinstance(analyzed, dict):
                    results.append(analyzed)
                else:
                    self.logger.warning(f"{self.get_name()} returned invalid type at index {idx}")
            except Exception as e:
                self.logger.warning(f"{self.get_name()} failed to analyze index {idx}: {e}")
        return results

    def analyze_one(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        return self.analyze([artifact])[0]

    def enrich_result(self, artifact: Dict[str, Any], matched: Union[str, List[str]], severity: Optional[int] = None) -> Dict[str, Any]:
        result = copy.deepcopy(artifact)
        result.setdefault("analysis", {})
        if isinstance(matched, str):
            matched = [matched]
        existing = set(result["analysis"].get("matched_rules", []))
        result["analysis"]["matched_rules"] = list(existing.union(matched))
        if severity is not None:
            result["analysis"]["severity"] = max(severity, result["analysis"].get("severity", 0))
        return result

    def set_severity_map(self, mapping: Dict[str, int]):
        self._severity_map = mapping

    def get_severity_for_rule(self, rule_id: str) -> int:
        return self._severity_map.get(rule_id, 1)

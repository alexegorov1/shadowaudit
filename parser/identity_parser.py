from typing import List, Dict, Any
from parser.base_parser import BaseParser

class IdentityParser(BaseParser):
    def get_name(self) -> str:
        return "identity_parser"

    def supported_types(self) -> List[str]:
        return ["*"]

    def parse(self, raw_artifact: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(raw_artifact, dict):
            self.logger.warning(f"[{self._name}] Skipped non-dict artifact: {type(raw_artifact).__name__}")
            return {}

        artifact = raw_artifact.copy()
        host_id = artifact.get("host_id", "unknown_host")

        missing = self._check_required_fields(artifact)
        if missing:
            self.logger.warning(f"[{self._name}] Missing fields from host='{host_id}': {sorted(missing)}")

        if self.logger.isEnabledFor(10):
            self.logger.debug(f"[{self._name}] passthrough: {self._debug_artifact_id(artifact)}")

        artifact["normalized_by"] = self._name
        return artifact

    def _check_required_fields(self, artifact: Dict[str, Any]) -> set[str]:
        required = {"host_id", "source", "collected_at", "artifact_type", "confidence", "evidence_type"}
        return required - artifact.keys()

    def _debug_artifact_id(self, artifact: Dict[str, Any]) -> str:
        rid = artifact.get("file_path") or artifact.get("artifact_type") or "unknown"
        return f"host={artifact.get('host_id', '?')} type={artifact.get('artifact_type', '?')} id={rid}"

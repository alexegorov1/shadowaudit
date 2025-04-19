from typing import List, Dict, Any
from parser.base_parser import BaseParser

class IdentityParser(BaseParser):
    def get_name(self) -> str:
        return "identity_parser"

    def supported_types(self) -> List[str]:
        return ["*"]

    def parse(self, raw_artifact: Dict[str, Any]) -> Dict[str, Any]:
        artifact = dict(raw_artifact)
        artifact_id = artifact.get("file_path") or artifact.get("artifact_type") or "unknown"
        host_id = artifact.get("host_id", "unknown_host")

        required = {"host_id", "source", "collected_at", "artifact_type", "confidence", "evidence_type"}
        missing = required - artifact.keys()

        if missing:
            self.logger.warning(f"[{self._name}] Missing required fields from host '{host_id}': {sorted(missing)}")

        if self.logger.isEnabledFor(10):
            self.logger.debug(
                f"[{self._name}] passthrough: host={host_id} type={artifact.get('artifact_type')} id={artifact_id}"
            )

        return artifact

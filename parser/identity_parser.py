from typing import List, Dict, Any
from parser.base_parser import BaseParser
import copy

class IdentityParser(BaseParser):
    def get_name(self) -> str:
        return "identity_parser"

    def supported_types(self) -> List[str]:
        return ["*"]

    def parse(self, raw_artifact: Dict[str, Any]) -> Dict[str, Any]:
        artifact = copy.deepcopy(raw_artifact)
        artifact_id = artifact.get("file_path") or artifact.get("artifact_type") or "unknown"
        host_id = artifact.get("host_id", "unknown_host")
        required_fields = ["host_id", "source", "collected_at", "artifact_type", "confidence", "evidence_type"]
        missing = [field for field in required_fields if field not in artifact]
        if missing:
            self.logger.warning(f"{self.get_name()} missing required fields from host '{host_id}': {missing}")
        if self.logger.isEnabledFor(10):
            self.logger.debug(f"{self.get_name()} passthrough: host={host_id} type={artifact.get('artifact_type')} id={artifact_id}")
        return artifact

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging


class BaseParser(ABC):
    def __init__(self) -> None:
        self._logger = None

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def supported_types(self) -> List[str]:
        pass

    @abstractmethod
    def parse(self, raw_artifact: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def should_parse(self, artifact: Dict[str, Any]) -> bool:
        try:
            target_type = artifact.get("artifact_type", "").lower()
            supported = self.supported_types()
            return "*" in supported or target_type in supported
        except Exception as e:
            self.logger.warning(f"[{self.get_name()}] Type check failed: {e}")
            return False

    def process_all(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed = []
        for idx, artifact in enumerate(artifacts):
            if not self.should_parse(artifact):
                continue
            try:
                result = self.parse(artifact)
                if isinstance(result, dict):
                    processed.append(result)
                else:
                    self.logger.warning(f"[{self.get_name()}][#{idx}] Non-dict returned")
            except Exception as e:
                self.logger.warning(f"[{self.get_name()}][#{idx}] Parse error: {e}")
        return processed

    @property
    def logger(self) -> logging.Logger:
        if not self._logger:
            self._logger = logging.getLogger(f"shadowaudit.parser.{self.get_name()}")
        return self._logger

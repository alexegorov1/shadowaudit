from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging


class BaseParser(ABC):
    def __init__(self) -> None:
        self._logger = None
        self._name = self.get_name()
        self._supported = set(t.lower() for t in self.supported_types())

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
            t = artifact.get("artifact_type", "").lower()
            return "*" in self._supported or t in self._supported
        except Exception as e:
            self.logger.warning(f"[{self._name}] should_parse() error: {e}")
            return False

    def process_all(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed = []
        for idx, artifact in enumerate(artifacts):
            if not self.should_parse(artifact):
                continue
            try:
                result = self.parse(artifact)
                if isinstance(result, dict):
                    parsed.append(result)
                else:
                    self.logger.warning(f"[{self._name}][#{idx}] parse() returned non-dict")
            except Exception as e:
                self.logger.warning(f"[{self._name}][#{idx}] parse() failed: {e}")
        return parsed

    @property
    def logger(self) -> logging.Logger:
        if not self._logger:
            self._logger = logging.getLogger(f"shadowaudit.parser.{self._name}")
        return self._logger

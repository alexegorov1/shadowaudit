from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging


class BaseParser(ABC):
    def __init__(self) -> None:
        self._logger: logging.Logger = None
        self._supported_cache: set[str] = None

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
            artifact_type = artifact.get("artifact_type")
            if not isinstance(artifact_type, str):
                return False
            artifact_type = artifact_type.lower()
            return "*" in self.supported_set or artifact_type in self.supported_set
        except Exception as e:
            self.logger.warning(f"[{self.get_name()}] should_parse() error: {e}")
            return False

    def process_all(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        output: List[Dict[str, Any]] = []
        for idx, artifact in enumerate(artifacts):
            if not self.should_parse(artifact):
                continue
            try:
                result = self.parse(artifact)
                if isinstance(result, dict):
                    output.append(result)
                else:
                    self.logger.warning(f"[{self.get_name()}][#{idx}] parse() returned non-dict")
            except Exception as e:
                self.logger.warning(f"[{self.get_name()}][#{idx}] parse() failed: {e}")
        return output

    @property
    def supported_set(self) -> set[str]:
        if self._supported_cache is None:
            try:
                types = self.supported_types()
                self._supported_cache = set(t.lower() for t in types if isinstance(t, str))
            except Exception as e:
                self.logger.error(f"[{self.get_name()}] failed to initialize supported_types: {e}")
                self._supported_cache = set()
        return self._supported_cache

    @property
    def logger(self) -> logging.Logger:
        if self._logger is None:
            self._logger = logging.getLogger(f"shadowaudit.parser.{self.get_name()}")
        return self._logger

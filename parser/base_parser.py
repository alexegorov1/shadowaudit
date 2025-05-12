from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging


class BaseParser(ABC):
    def __init__(self) -> None:
        self._logger: logging.Logger = None
        self._name: str = self.get_name()
        supported = self.supported_types()
        self._supported: set[str] = set(t.lower() for t in supported if isinstance(t, str))

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
            artifact_type = artifact.get("artifact_type", "").strip().lower()
            return "*" in self._supported or artifact_type in self._supported
        except Exception as e:
            self.logger.warning(f"[{self._name}] should_parse() error: {e}")
            return False

        if self._logger is None:
            self._logger = logging.getLogger(f"shadowaudit.parser.{self._name}")
        return self._logger

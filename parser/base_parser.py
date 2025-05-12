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


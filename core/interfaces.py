from abc import ABC, abstractmethod
from typing import List, Dict

class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> List[Dict]:
        """Collects and returns a list of artifact dictionaries."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Returns the unique name of the collector module."""
        pass

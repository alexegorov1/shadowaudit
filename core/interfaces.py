from abc import ABC, abstractmethod
from typing import List, Dict

class BaseCollector(ABC):
    @abstractmethod
    def collect(self) -> List[Dict]:
        """Collects and returns a list of artifact dictionaries."""
        pass

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

class BaseParser(ABC):
    """
    Abstract base class for all artifact parsers in ShadowAudit.
    Parsers are responsible for normalizing raw artifact fields and
    optionally enriching data with derived or external context.
    """

    def __init__(self):
        self.logger = self.get_logger()

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the unique name of the parser module.
        """
        pass

    @abstractmethod
    def supported_types(self) -> List[str]:
        """
        Returns a list of artifact_type values this parser can process.
        Use ["*"] to indicate universal applicability.
        """
        pass

    @abstractmethod
    def parse(self, raw_artifact: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts a single raw artifact and returns a normalized artifact dictionary.
        This method is called only if should_parse() returns True.
        """
        pass

    def should_parse(self, artifact: Dict[str, Any]) -> bool:
        """
        Determines whether this parser should process the given artifact.
        Default implementation checks artifact_type field.
        """
        try:
            artifact_type = artifact.get("artifact_type", "").lower()
            return "*" in self.supported_types() or artifact_type in self.supported_types()
        except Exception as e:
            self.logger.warning(f"{self.get_name()} parser failed type check: {e}")
            return False

    def process_all(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies parse() to all applicable artifacts.
        Skips and logs any parsing errors.
        """
        result = []
        for idx, art in enumerate(artifacts):
            if not self.should_parse(art):
                continue
            try:
                parsed = self.parse(art)
                if isinstance(parsed, dict):
                    result.append(parsed)
                else:
                    self.logger.warning(f"{self.get_name()} returned non-dict at index {idx}")
            except Exception as e:
                self.logger.warning(f"{self.get_name()} failed to parse artifact at index {idx}: {e}")
        return result

    def get_logger(self) -> logging.Logger:
        """
        Returns a standard logger named after the parser class.
        """
        return logging.getLogger(f"shadowaudit.parser.{self.get_name()}")

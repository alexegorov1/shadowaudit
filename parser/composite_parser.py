from typing import List, Dict, Any, Set
from parser.base_parser import BaseParser

class CompositeParser(BaseParser):
    def __init__(self, name: str = "composite_parser"):
        self._name = name
        self._logger = None
        self._parsers: List[BaseParser] = []
        self._parser_ids: Set[int] = set()

    def get_name(self) -> str:
        return self._name

    def supported_types(self) -> List[str]:
        return ["*"]

    def add_parser(self, parser: BaseParser) -> None:
        pid = id(parser)
        if pid in self._parser_ids:
            self.logger.warning(f"[{self._name}] Parser already added: {parser.get_name()}")
            return
        self._parsers.append(parser)
        self._parser_ids.add(pid)
        self.logger.info(f"[{self._name}] Registered parser: {parser.get_name()}")


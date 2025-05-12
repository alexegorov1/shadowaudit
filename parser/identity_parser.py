from typing import List, Dict, Any
from parser.base_parser import BaseParser

class IdentityParser(BaseParser):
    def get_name(self) -> str:
        return "identity_parser"

    def supported_types(self) -> List[str]:
        return ["*"]

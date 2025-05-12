from typing import Any, Dict, Optional
from enum import Enum
from datetime import datetime


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    FATAL = "fatal"


class ParserError:
    def __init__(
        self,
        parser_name: str,
        artifact_index: int,
        artifact_id: str,
        error_type: str,
        message: str,
        field: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None,
        severity: Severity = Severity.MEDIUM,
        timestamp: Optional[str] = None,
    ) -> None:
        self.parser_name = parser_name
        self.artifact_index = artifact_index
        self.artifact_id = artifact_id
        self.error_type = error_type
        self.message = message
        self.field = field
        self.expected_type = expected_type
        self.actual_value = actual_value
        self.severity = severity
        self.timestamp = timestamp or datetime.utcnow().isoformat()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "parser": self.parser_name,
            "index": self.artifact_index,
            "artifact_id": self.artifact_id,
            "error_type": self.error_type,
            "message": self.message,
            "field": self.field,
            "expected_type": self.expected_type,
            "actual_value": self.actual_value,
            "severity": self.severity,
            "timestamp": self.timestamp
        }

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.parser_name}#{self.artifact_index}: {self.message}"


class FieldMissingError(ParserError):
    def __init__(self, parser_name: str, artifact_index: int, artifact_id: str, field: str):
        super().__init__(
            parser_name=parser_name,
            artifact_index=artifact_index,
            artifact_id=artifact_id,
            error_type="FieldMissing",
            message=f"Required field '{field}' is missing",
            field=field,
            severity=Severity.HIGH
        )


class TypeMismatchError(ParserError):
    def __init__(
        self, parser_name: str, artifact_index: int, artifact_id: str,
        field: str, expected_type: str, actual_value: Any
    ):
        super().__init__(
            parser_name=parser_name,
            artifact_index=artifact_index,
            artifact_id=artifact_id,
            error_type="TypeMismatch",
            message=f"Expected type '{expected_type}' for field '{field}', got value: {repr(actual_value)}",
            field=field,
            expected_type=expected_type,
            actual_value=actual_value,
            severity=Severity.MEDIUM
        )


class UnexpectedValueError(ParserError):
    def __init__(
        self, parser_name: str, artifact_index: int, artifact_id: str,
        field: str, actual_value: Any
    ):
        super().__init__(
            parser_name=parser_name,
            artifact_index=artifact_index,
            artifact_id=artifact_id,
            error_type="UnexpectedValue",
            message=f"Unexpected value in field '{field}': {repr(actual_value)}",
            field=field,
            actual_value=actual_value,
            severity=Severity.MEDIUM
        )


class ParseCrashError(ParserError):
    def __init__(
        self, parser_name: str, artifact_index: int, artifact_id: str, exception: Exception
    ):
        super().__init__(
            parser_name=parser_name,
            artifact_index=artifact_index,
            artifact_id=artifact_id,
            error_type="Exception",
            message=str(exception),
            severity=Severity.FATAL
        )

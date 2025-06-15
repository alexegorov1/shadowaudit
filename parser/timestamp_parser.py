import logging
from typing import Optional
from datetime import datetime
import dateutil.parser
import pytz

class TimestampParser:
    def __init__(self, fallback_timezone: str = "UTC"):
        self.logger = logging.getLogger("shadowaudit.parser.timestamp_parser")
        self.default_tz = pytz.timezone(fallback_timezone)

    def parse_timestamp(self, raw: str, prefer_utc: bool = True) -> Optional[str]:
        if not isinstance(raw, str) or not raw.strip():
            self.logger.debug(f"Empty or invalid timestamp input: {raw}")
            return None
        try:
            parsed = dateutil.parser.parse(raw)
            if not parsed.tzinfo:
                parsed = self.default_tz.localize(parsed)
            if prefer_utc:
                parsed = parsed.astimezone(pytz.UTC)
            return parsed.isoformat()
        except (ValueError, OverflowError) as e:
            self.logger.warning(f"Failed to parse timestamp: {raw} ({e})")
            return None

    def normalize_artifact_timestamp(self, artifact: dict, field: str = "collected_at") -> dict:
        original = artifact.get(field)
        normalized = self.parse_timestamp(original)
        if normalized:
            artifact[field] = normalized
        else:
            self.logger.warning(f"[{artifact.get('artifact_type', 'unknown')}] Invalid timestamp in field '{field}': {original}")
        return artifact

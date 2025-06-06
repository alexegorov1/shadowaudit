from typing import List, Dict, Any, Optional, Union
from reporter.base_reporter import BaseReporter
import json
import os
import datetime
import uuid
import gzip

class JSONReporter(BaseReporter):
    def __init__(
        self,
        output_dir: Optional[str] = "results",
        include_summary: bool = True,
        split_by_type: bool = False,
        indent: int = 2,
        compress: bool = False,
        pretty_print: bool = True,
        filter_high_severity: bool = False
    ):
        super().__init__(output_dir=output_dir, filename_prefix="json_report")
        self.include_summary = include_summary
        self.split_by_type = split_by_type
        self.indent = indent if pretty_print else None
        self.compress = compress
        self.pretty = pretty_print
        self.filter_high_severity = filter_high_severity

    def generate(self, artifacts: List[Dict[str, Any]]) -> None:
        if not artifacts:
            self.logger.info("No artifacts to report.")
            return

        output_paths = []
        data = artifacts
        if self.filter_high_severity:
            data = self.filter_by_severity(artifacts)

        if self.split_by_type:
            grouped = self.group_by_type(data)
            for artifact_type, group in grouped.items():
                path = self._write(group, f"{self.filename_prefix}_{artifact_type}")
                if path:
                    output_paths.append(path)
        else:
            path = self._write(data, self.filename_prefix)
            if path:
                output_paths.append(path)

        if self.include_summary:
            summary = self.summarize(data)
            summary_path = self._write(summary, f"{self.filename_prefix}_summary")
            if summary_path:
                output_paths.append(summary_path)

        self.logger.info(f"JSONReporter completed: {len(output_paths)} files written.")

    def _write(self, data: Union[List[Dict[str, Any]], Dict[str, Any]], prefix: str) -> Optional[str]:
        filename = self._generate_filename(prefix)
        full_path = os.path.join(self.output_dir, filename)
        try:
            if self.compress:
                full_path += ".gz"
                with gzip.open(full_path, "wt", encoding="utf-8") as f:
                    json.dump(data, f, indent=self.indent, ensure_ascii=False)
            else:
                with open(full_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=self.indent, ensure_ascii=False)
            self.logger.debug(f"Wrote {len(data) if isinstance(data, list) else 1} record(s) to {full_path}")
            return full_path
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {full_path}: {e}")
            return None

    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        uid = uuid.uuid4().hex[:6]
        return f"{prefix}_{timestamp}_{uid}.json"

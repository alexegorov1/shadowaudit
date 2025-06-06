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

    def _generate_filename(self, prefix: str) -> str:
        timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        uid = uuid.uuid4().hex[:6]
        return f"{prefix}_{timestamp}_{uid}.json"

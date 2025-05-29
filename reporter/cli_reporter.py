from typing import List, Dict, Any, Optional
from reporter.base_reporter import BaseReporter
from rich.console import Console
from rich.progress import track
from rich import box
import os
import datetime

class CLIReporter(BaseReporter):
    def __init__(
        self,
        output_dir: Optional[str] = "results",
        show_summary: bool = True,
        show_details: bool = True,
        severity_threshold: int = 0,
        interactive: bool = False,
        max_display: int = 100,
        pause_after: Optional[int] = None
    ):
        super().__init__(output_dir=output_dir, filename_prefix="cli_report")
        self.console = Console()
        self.show_summary = show_summary
        self.show_details = show_details
        self.severity_threshold = severity_threshold
        self.interactive = interactive
        self.max_display = max_display
        self.pause_after = pause_after

    def get_name(self) -> str:
        return "cli_reporter"

    def generate(self, artifacts: List[Dict[str, Any]]) -> None:
        if not artifacts:
            self.console.print("[bold yellow]No artifacts to display.[/bold yellow]")
            return

        filtered = [a for a in artifacts if a.get("analysis", {}).get("severity", 0) >= self.severity_threshold]

        if self.show_summary:
            summary = self.summarize(filtered)
            self._render_summary(summary)

        if self.show_details:
            if self.interactive:
                filtered = self._interactive_filter(filtered)
            self._render_table(filtered)

    def _render_summary(self, summary: Dict[str, Any]) -> None:
        text = Text()
        timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        text.append(f"\n[SUMMARY @ {timestamp}]\n", style="bold underline")
        for key, value in summary.items():
            text.append(f"{key.replace('_', ' ').capitalize()}: {value}\n")
        self.console.print(Panel(text, title="Artifact Summary", expand=False, border_style="cyan"))

    def _render_table(self, artifacts: List[Dict[str, Any]]) -> None:
        table = Table(title="Collected Artifacts", box=box.MINIMAL_DOUBLE_HEAD)
        table.add_column("Index", style="dim", width=6)
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Path/Source", style="white")
        table.add_column("Severity", style="bold")
        table.add_column("Confidence", style="green")
        table.add_column("Rules", style="magenta")

        count = 0
        for i, art in enumerate(track(artifacts[:self.max_display], description="Rendering table...")):
            art_type = art.get("artifact_type", "unknown")
            path = art.get("file_path", art.get("source", "-"))
            severity = str(art.get("analysis", {}).get("severity", "-"))
            confidence = f"{art.get('confidence', 0):.2f}"
            rules = ", ".join(art.get("analysis", {}).get("matched_rules", [])) if "analysis" in art else "-"
            sev_style = "red" if severity != "-" and int(severity) >= 4 else "yellow" if severity != "-" and int(severity) >= 2 else "green"
            table.add_row(str(i), art_type, path, f"[{sev_style}]{severity}[/{sev_style}]", confidence, rules)
            count += 1
            if self.pause_after and count % self.pause_after == 0:
                if not Confirm.ask("Continue displaying more artifacts?"):
                    break

        self.console.print(table)

    def _interactive_filter(self, artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.console.print("\n[bold]Interactive Filtering Activated[/bold]\n", style="blue")
        confirmed = Confirm.ask("Only show artifacts with matched rules?")
        if confirmed:
            artifacts = [a for a in artifacts if a.get("analysis", {}).get("matched_rules")]
        confirmed = Confirm.ask("Only show high severity artifacts?")
        if confirmed:
            artifacts = [a for a in artifacts if a.get("analysis", {}).get("severity", 0) >= 4]
        return artifacts

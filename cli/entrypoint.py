import argparse
import sys
import importlib
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory


_PHASES = {
    "collect": ("agent.main_runner", "run_collection_phase"),
    "analyze": ("analyzer.orchestrator", "run_analysis_phase"),
    "report": ("reporter.orchestrator", "run_report_phase"),
}

def _import_phase_handler(phase: str):
    if phase not in _PHASES:
        print(f"[FATAL] Unknown command: '{phase}'")
        sys.exit(2)
    module_name, function_name = _PHASES[phase]
    try:
        module = importlib.import_module(module_name)
        return getattr(module, function_name)
    except Exception as e:
        print(f"[FATAL] Failed to load handler for '{phase}': {e}")
        sys.exit(3)


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        prog="shadowaudit",
        description="ShadowAudit — Forensic Artifact Framework"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    for phase in _PHASES:
        subparsers.add_parser(phase, help=f"Run the '{phase}' phase")

    args = parser.parse_args()
    handler = _import_phase_handler(args.command)
    config = _load_config(args.config)
    logger = LoggerFactory(config.get("general", {})).create_logger("shadowaudit.cli")

    logger.info(f"[INIT] Starting phase: {args.command}")
    try:
        handler(config)
    except Exception as e:
        logger.error(f"[{args.command.upper()}] Execution failed: {e}")
        sys.exit(1)

    logger.info(f"[DONE] Phase '{args.command}' completed successfully")

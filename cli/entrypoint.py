import argparse
import sys
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory


def _load_config(path: str) -> dict:
    try:
        return ConfigLoader(path).full
    except Exception as e:
        print(f"[FATAL] Failed to load config from '{path}': {e}")
        sys.exit(1)


def _phase_dispatcher() -> dict:
    return {
        "collect": lambda config: __import__("agent.main_runner").agent.main_runner.run_collection_phase(config),
        "analyze": lambda config: __import__("analyzer.orchestrator").analyzer.orchestrator.run_analysis_phase(config),
        "report": lambda config: __import__("reporter.orchestrator").reporter.orchestrator.run_report_phase(config),
    }


def _run_phase(phase: str, config: dict) -> None:
    dispatch = _phase_dispatcher()
    if phase not in dispatch:
        raise ValueError(f"[FATAL] Unsupported command: '{phase}'")
    try:
        dispatch[phase](config)
    except Exception as e:
        raise RuntimeError(f"[{phase.upper()}] Phase execution failed: {e}")


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
    for name in _phase_dispatcher().keys():
        subparsers.add_parser(name, help=f"Run '{name}' phase")

    args = parser.parse_args()
    config = _load_config(args.config)

    logger = LoggerFactory(config.get("general", {})).create_logger("shadowaudit.cli")
    logger.info(f"[INIT] ShadowAudit CLI started — phase: {args.command}")

    try:
        _run_phase(args.command, config)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"[DONE] Phase completed: {args.command}")

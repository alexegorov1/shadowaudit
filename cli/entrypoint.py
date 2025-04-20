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


def _run_phase(phase: str, config: dict) -> None:
    try:
        if phase == "collect":
            from agent.main_runner import run_collection_phase
            run_collection_phase(config)

        elif phase == "analyze":
            from analyzer.orchestrator import run_analysis_phase
            run_analysis_phase(config)

        elif phase == "report":
            from reporter.orchestrator import run_report_phase
            run_report_phase(config)

        else:
            raise ValueError(f"Unsupported command: {phase}")

    except Exception as e:
        raise RuntimeError(f"[{phase.upper()}] Phase failed: {e}")


def run_cli() -> None:
    parser = argparse.ArgumentParser(
        prog="shadowaudit",
        description="ShadowAudit — Automated forensic artifact processing"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("collect", "analyze", "report"):
        subparsers.add_parser(name, help=f"Run {name} phase")

    args = parser.parse_args()
    config = _load_config(args.config)

    logger = LoggerFactory(config.get("general", {})).create_logger("shadowaudit.cli")
    logger.info(f"Starting ShadowAudit CLI — phase: {args.command}")

    try:
        _run_phase(args.command, config)
    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"Completed: {args.command} phase")

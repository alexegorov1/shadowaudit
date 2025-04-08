import argparse
import sys
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory

def _load_config(path: str = "config.yaml"):
    try:
        return ConfigLoader(path).full
    except Exception as e:
        print(f"[FATAL] Cannot load config: {e}")
        sys.exit(1)

def _run_collect(config: dict):
    from agent.main_runner import run_collection_phase
    try:
        run_collection_phase(config)
    except Exception as e:
        raise RuntimeError(f"Collection phase failed: {e}")

def _run_analyze(config: dict):
    from analyzer.orchestrator import run_analysis_phase
    try:
        run_analysis_phase(config)
    except Exception as e:
        raise RuntimeError(f"Analysis phase failed: {e}")

def _run_report(config: dict):
    from reporter.orchestrator import run_report_phase
    try:
        run_report_phase(config)
    except Exception as e:
        raise RuntimeError(f"Report generation failed: {e}")

def run_cli():
    parser = argparse.ArgumentParser(
        prog="shadowaudit",
        description="ShadowAudit - Forensic Artifact Framework"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("collect", help="Run collection phase")
    subparsers.add_parser("analyze", help="Run analysis phase")
    subparsers.add_parser("report", help="Run report generation")

    args = parser.parse_args()
    config = _load_config(args.config)
    logger = LoggerFactory(config.get("general", {})).create_logger("shadowaudit.cli")

    try:
        if args.command == "collect":
            logger.info("Launching collection phase")
            _run_collect(config)

        elif args.command == "analyze":
            logger.info("Launching analysis phase")
            _run_analyze(config)

        elif args.command == "report":
            logger.info("Launching report phase")
            _run_report(config)

    except Exception as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"ShadowAudit CLI execution completed: {args.command}")

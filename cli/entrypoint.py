import argparse
import sys
from core.config_loader import ConfigLoader
from core.logger import LoggerFactory
from agent.main_runner import run_collection_phase
from analyzer.orchestrator import run_analysis_phase
from reporter.orchestrator import run_report_phase

def run_cli():
    parser = argparse.ArgumentParser(
        description="ShadowAudit CLI - Forensic artifact collection and analysis"
    )
    parser.add_argument("--collect", action="store_true", help="Run artifact collection phase")
    parser.add_argument("--analyze", action="store_true", help="Run analysis phase")
    parser.add_argument("--report", action="store_true", help="Generate report from artifacts")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file")

    args = parser.parse_args()

    try:
        config_loader = ConfigLoader(args.config)
        config = config_loader.full
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)

    logger = LoggerFactory(config.get("general", {})).create_logger("shadowaudit.cli")

    if args.collect:
        logger.info("Starting collection phase")
        try:
            run_collection_phase(config)
        except Exception as e:
            logger.error(f"Collection phase failed: {e}")
            sys.exit(2)

    if args.analyze:
        logger.info("Starting analysis phase")
        try:
            run_analysis_phase(config)
        except Exception as e:
            logger.error(f"Analysis phase failed: {e}")
            sys.exit(3)

    if args.report:
        logger.info("Starting report generation")
        try:
            run_report_phase(config)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            sys.exit(4)

    if not (args.collect or args.analyze or args.report):
        logger.warning("No phase selected. Use --collect, --analyze, or --report.")
        parser.print_help()

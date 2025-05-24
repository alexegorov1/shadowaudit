import sys
import traceback
from cli.entrypoint import run_cli
from core.logger import Logger

def main():
    logger = Logger()

    try:
        run_cli()
    except KeyboardInterrupt:
        logger.log("Execution interrupted by user (KeyboardInterrupt).", level="warning")
        sys.exit(130)
    except SystemExit:
        raise

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
    except Exception as exc:
        exc_type = type(exc).__name__
        logger.log(f"Fatal exception occurred: {exc_type}: {exc}", level="critical")
        tb = traceback.format_exc(limit=5, chain=False)
        logger.log(tb, level="debug")
        sys.exit(1)

if __name__ == "__main__":
    main()

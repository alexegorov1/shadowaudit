import sys
from core.logger import LoggerFactory
from core.config_loader import ConfigLoader

def main():
    try:
        config = ConfigLoader().full
        logger = LoggerFactory(config.get("general", {})).create_logger("shadowaudit.main")
    except Exception as init_exc:
        print(f"[FATAL] Logger or config initialization failed: {init_exc}", file=sys.stderr)
        sys.exit(1)

    try:
        run_cli()
    except SystemExit:
        raise
    except Exception as exc:
        exc_type = type(exc).__name__
        logger.critical(f"Fatal exception occurred: {exc_type}: {exc}")
        tb = traceback.format_exc(limit=5, chain=False)
        logger.debug(tb)
        sys.exit(1)

if __name__ == "__main__":
    main()

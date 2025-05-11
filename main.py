import sys
import traceback
from cli.entrypoint import run_cli
def main():
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n[ABORTED] Execution interrupted by user.")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as exc:
        exc_type = type(exc).__name__
        print(f"\n[FATAL] {exc_type}: {exc}")
        traceback.print_exc(limit=5, chain=False)
        sys.exit(1)

if __name__ == "__main__":
    main()

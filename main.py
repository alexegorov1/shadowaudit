import sys
import traceback
from cli.entrypoint import run_cli

def main():
    try:
        run_cli()
    except KeyboardInterrupt:
        print("\n[ABORTED] Execution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"[FATAL] Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

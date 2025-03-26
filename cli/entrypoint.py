import argparse

def run_cli():
    parser = argparse.ArgumentParser(description="ShadowAudit CLI")
    parser.add_argument("--collect", action="store_true", help="Run artifact collection")
    parser.add_argument("--analyze", action="store_true", help="Run analysis phase")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to configuration file")

    args = parser.parse_args()

    if args.collect:
        print("Collection phase triggered")
    if args.analyze:
        print("Analysis phase triggered")
    if args.report:
        print("Report generation triggered")

# shadowaudit

ShadowAudit is a modular forensic analysis framework designed to help incident responders and forensic engineers identify residual artifacts of compromise on endpoint systems. It focuses not on active detection or prevention, but on post-compromise visibility—retrieving evidence that attackers may have removed or overlooked during cleanup.

The tool was built with practical DFIR workflows in mind. It allows analysts to collect, normalize, and analyze forensic artifacts left on a system, such as execution history, registry changes, orphaned scheduled tasks, WMI persistence, and more. These traces are frequently missed by traditional monitoring tools, especially when they occur outside of real-time visibility windows.

ShadowAudit provides a structured interface for collecting artifacts, validating and transforming them into normalized formats, applying rule-based or heuristic detection logic, and generating human-readable or machine-consumable reports. Everything is designed to be transparent, scriptable, extendable, and portable.

Purpose and Use Cases
This project exists to support scenarios where an attacker was present, but current indicators are inconclusive. It answers questions like: Was malware here earlier? Are there orphaned persistence mechanisms left behind? Are there inconsistencies in execution artifacts that point to tampering?

Typical use cases include post-incident investigation, validation of threat hunting hypotheses, review of potentially compromised systems, and evidence collection during controlled red team operations. ShadowAudit is not meant to replace SIEMs or EDRs, but rather to complement them where traditional telemetry is lacking or unavailable.

The tool can be deployed manually on endpoints or integrated into automated forensic triage workflows. It supports standalone CLI execution and is being developed with a future backend API model in mind.

Architecture and Design
The system is organized into isolated, composable modules that operate on clear responsibilities. Each component is a directory containing self-contained code and optionally submodules:

The agent layer initiates execution and handles coordination across the stack.

Collector modules are responsible for harvesting specific types of forensic data.

Parsers handle normalization, transforming raw inputs into structured schema-compliant documents.

Analyzers apply logic to infer suspicious patterns or anomalies across artifacts.

Reporters render output to different formats for use by analysts or machines.

CLI provides a command-line interface with basic execution routing.

Each layer is cleanly separated and communicates via Python interfaces. Components are loaded dynamically at runtime based on project structure and plugin registration patterns. Adding a new collector or analyzer does not require altering core code, which is intentional.

The platform was designed to work offline, to leave no operational trace on the target system, and to operate read-only unless explicitly configured otherwise.

Getting Started
To use ShadowAudit, you’ll need Python 3.10 or later. It is strongly recommended that you set up a virtual environment to isolate dependencies.

Once the environment is activated, install the project in editable mode. This allows live development and testing of all modules. Dependencies are minimal and listed in the project configuration.

All logic is driven by a configuration file (config.yaml) located in the project root. This file defines output paths, enabled collector modules, log levels, analysis thresholds, and output formatting preferences. If needed, a custom config can be passed via CLI.

Typical usage involves collecting data, analyzing it, and generating a report in sequence. Each phase can also be run independently. Output is written to the directory defined in the configuration under general.output_path.

Project Structure
The repository uses a modular structure that keeps responsibilities separated and code maintainable. The core directory contains shared logic, such as configuration loading, logging infrastructure, plugin discovery, and base interfaces. Each major function of the tool lives in its own subdirectory:

core/ contains framework-wide logic like logging and config parsing.

agent/ includes orchestration code for running ShadowAudit on a target.

collector/ implements data collectors for specific artifact types.

parser/ handles transforming raw collected data into normalized schema objects.

analyzer/ includes rule engines and correlation logic.

reporter/ supports output rendering in various formats including CLI, JSON, and HTML.

cli/ holds command-line interface logic for parsing arguments and routing execution.

schemas/ holds JSON schema definitions used to validate artifact structure.

tests/ includes all test logic covering individual components.

plugins/ is reserved for external or organization-specific extensions.

results/ is the output folder where collected and analyzed data is saved; excluded from Git.

Each module is independently testable, pluggable, and swappable. The interfaces are explicitly defined using Python’s abstract base class (ABC) pattern to enforce contracts between components.

Configuration
All behavior is defined in a single YAML configuration file. This includes:

Global settings like output path, logging level, or language

Collector module selection and exclusion paths

Analysis engine behavior, including whether heuristics are enabled and what score threshold to use

Report formats and rendering templates

No logic should ever hardcode file paths or system-specific assumptions. Everything should derive from the configuration. The system is designed to be transparent and easy to audit for operational or regulatory requirements.

Developer Expectations
Adding new functionality to ShadowAudit should be simple and predictable. Every module follows a clear structure:

Collectors must implement BaseCollector and define a collect() method.

Analyzers must implement BaseAnalyzer and define an analyze(data) method.

Reporters must implement BaseReporter and define a generate_report(results) method.

Plugins are registered automatically using dynamic discovery. There is no need to manually import a new module into the CLI or core runtime.

All modules should avoid state retention across executions, should use logging instead of print statements, and should follow the structure and naming conventions already present in the codebase. Logging is centralized and supports both file and stdout modes, with configurable log levels.

Tests should be created alongside every new module. Tests must be self-contained, not rely on external systems or networks, and use temporary directories for file operations. All core functionality is tested using pytest, with standard Python test discovery.

Working with the Codebase
Developers contributing to ShadowAudit are expected to:

Use type hints and docstrings where clarity is improved

Avoid tightly coupling code across layers

Follow existing module patterns and structure

Extend the configuration system instead of bypassing it

Commit with clear, meaningful messages

Write modular, small functions with a single responsibility

Every component in the system should be composable and overrideable. The goal is for contributors to build their own plugins, modules, or even new analysis pipelines without ever needing to fork or rewrite core functionality.

Testing and Validation
The platform uses pytest for testing. Tests are located under the tests/ directory and can be executed directly from the project root. All tests are designed to run locally, offline, and without modifying the system they execute on.

All functional units of the application—config parsing, logger setup, plugin loading, schema validation—have corresponding tests. Additional test cases should be added when new edge cases or modules are introduced.

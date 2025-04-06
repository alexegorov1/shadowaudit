import os
import tempfile
import pytest
from core.config_loader import ConfigLoader

valid_config = """
general:
  output_path: ./results
  log_level: INFO
  language: en
  suppress_stdout: false

collector:
  enabled_modules: [filesystem]
  exclude_paths: ["/tmp"]
  max_depth: 3

analyzer:
  enable_heuristics: true
  confidence_threshold: 0.6

reporter:
  formats: [json]
  template_path: ./templates
"""

invalid_config_missing_sections = """
general:
  output_path: ./results
"""

invalid_config_wrong_types = """
general:
  output_path: 12345
  log_level: true

collector:
  enabled_modules: "filesystem"
"""

empty_config = ""


def test_config_load_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(valid_config)

        loader = ConfigLoader(path)
        config = loader.full
        assert isinstance(config, dict)
        assert "general" in config
        assert config["general"]["log_level"] == "INFO"
        assert config["collector"]["enabled_modules"] == ["filesystem"]


def test_config_missing_file():
    with pytest.raises(FileNotFoundError):
        ConfigLoader("/nonexistent/path/config.yaml")


def test_config_structure_validation():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(valid_config)

        loader = ConfigLoader(path)
        collector = loader.get("collector")
        assert isinstance(collector["enabled_modules"], list)
        assert isinstance(collector["exclude_paths"], list)
        assert isinstance(collector["max_depth"], int)
        assert loader.get("reporter", {}).get("formats") == ["json"]


def test_config_empty_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(empty_config)

        loader = ConfigLoader(path)
        config = loader.full
        assert isinstance(config, dict)
        assert config == {}


def test_config_missing_sections_graceful_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(invalid_config_missing_sections)

        loader = ConfigLoader(path)
        assert "general" in loader.full
        assert loader.get("analyzer", default={"enable_heuristics": False})["enable_heuristics"] is False


def test_config_wrong_types_handling():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(invalid_config_wrong_types)

        loader = ConfigLoader(path)
        general = loader.get("general")
        collector = loader.get("collector")
        assert isinstance(general["output_path"], int)
        assert isinstance(general["log_level"], bool)
        assert isinstance(collector["enabled_modules"], str)

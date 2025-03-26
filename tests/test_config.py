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

def test_config_load_success():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(valid_config)

        loader = ConfigLoader(path)
        config = loader.full
        assert "general" in config
        assert config["general"]["log_level"] == "INFO"

def test_config_missing_file():
    with pytest.raises(FileNotFoundError):
        ConfigLoader("/nonexistent/path/config.yaml")

def test_config_structure_validation():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(valid_config)

        loader = ConfigLoader(path)
        assert "collector" in loader.full
        assert isinstance(loader.full["collector"]["enabled_modules"], list)

import os
import tempfile
import pytest
from core.config_loader import ConfigLoader

VALID_CONFIG = """
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

INVALID_CONFIG_MISSING = """
general:
  output_path: ./results
"""

INVALID_CONFIG_TYPES = """
general:
  output_path: 12345
  log_level: true

collector:
  enabled_modules: "filesystem"
"""

EMPTY_CONFIG = ""


def write_config(content: str) -> str:
    tmp = tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False)
    tmp.write(content)
    tmp.flush()
    tmp.close()
    return tmp.name


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        ConfigLoader("/nonexistent/file.yaml")


def test_partial_structure_access():
    path = write_config(INVALID_CONFIG_MISSING)
    loader = ConfigLoader(path)
    assert loader.get("analyzer", {"enable_heuristics": False})["enable_heuristics"] is False


def test_empty_config_fallback():
    path = write_config(EMPTY_CONFIG)
    loader = ConfigLoader(path)
    assert loader.full == {}
    assert loader.get("collector") is None


def test_wrong_types_present_but_not_blocking():
    path = write_config(INVALID_CONFIG_TYPES)
    loader = ConfigLoader(path)
    general = loader.get("general")
    assert isinstance(general["output_path"], int)
    assert isinstance(general["log_level"], bool)
    assert isinstance(loader.get("collector")["enabled_modules"], str)


def test_get_returns_default_if_missing():
    path = write_config(VALID_CONFIG)
    loader = ConfigLoader(path)
    assert loader.get("nonexistent") is None
    assert loader.get("nonexistent", default={"key": 123}) == {"key": 123}

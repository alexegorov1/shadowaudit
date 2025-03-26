import os
import yaml

class ConfigLoader:
    def __init__(self, path="config.yaml"):
        self._config_path = os.path.abspath(path)
        if not os.path.exists(self._config_path):
            raise FileNotFoundError(f"Config file not found: {self._config_path}")
        self._config = self._load()

    def _load(self):
        with open(self._config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def get(self, section, default=None):
        return self._config.get(section, default)

    @property
    def full(self):
        return self._config

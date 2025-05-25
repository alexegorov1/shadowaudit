import os
import yaml

class ConfigLoader:
    _instances = {}

    def __new__(cls, path="config.yaml"):
        abs_path = os.path.abspath(path)
        if abs_path not in cls._instances:
            obj = super().__new__(cls)
            obj._load(abs_path)
            cls._instances[abs_path] = obj
        return cls._instances[abs_path]

    def _load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary at root level")
            self._config = config
            self._path = path

    def get(self, section, default=None):
        return self._config.get(section, default)

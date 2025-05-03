import os
import yaml

class ConfigLoader:
    _instances = {}

    def __new__(cls, path="config.yaml"):
        path = os.path.abspath(path)
        if path not in cls._instances:
            obj = super().__new__(cls)
            obj._load_config(path)
            cls._instances[path] = obj
        return cls._instances[path]

    def _load_config(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Configuration root must be a dictionary")
            self._config = config

    def get(self, section, default=None):
        return self._config.get(section, default)

    @property
    def full(self):
        return self._config

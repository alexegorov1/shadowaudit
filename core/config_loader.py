import os
import yaml

class ConfigLoader:
    _instance = None

    def __new__(cls, path="config.yaml"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_config(path)
        return cls._instance

    def _init_config(self, path):
        self._config_path = os.path.abspath(path)
        if not os.path.isfile(self._config_path):
            raise FileNotFoundError(f"Configuration file not found at: {self._config_path}")
        self._config = self._load_config()

    def _load_config(self):
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ValueError("Configuration root must be a dictionary")
                return config
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML configuration: {e}") from e

    def get(self, section, default=None):
        return self._config.get(section, default)

    @property
    def full(self):
        return self._config


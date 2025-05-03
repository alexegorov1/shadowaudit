import os
import yaml

class ConfigLoader:
    _instance = None

    def __new__(cls, path="config.yaml"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(path)
        return cls._instance

    def _initialize(self, path):
        self._path = os.path.abspath(path)
        if not os.path.isfile(self._path):
            raise FileNotFoundError(f"Config not found at: {self._path}")
        self._config = self._load()

    def _load(self):
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ValueError("Top-level config must be a dict")
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parse error: {e}") from e

    def get(self, section, default=None):
        return self._config.get(section, default)

    @property
    def full(self):
        return self._config

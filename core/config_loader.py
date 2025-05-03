import os
import yaml

class ConfigLoader:
    _instance = {}

    def __new__(cls, path="config.yaml"):
        abs_path = os.path.abspath(path)
        if abs_path not in cls._instance:
            instance = super().__new__(cls)
            instance._initialize(abs_path)
            cls._instance[abs_path] = instance
        return cls._instance[abs_path]

    def _initialize(self, path):
        self._path = path
        if not os.path.isfile(self._path):
            raise FileNotFoundError(f"Config not found at: {self._path}")
        self._config = self._load()

    def _load(self):
        with open(self._path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Top-level config must be a dictionary")
            return config

    def get(self, section, default=None):
        return self._config.get(section, default)

    @property
    def full(self):
        return self._config
    @property
    def full(self):
        return self._config

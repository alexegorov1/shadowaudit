import os
import yaml

class ConfigLoader:
    _cache = {}

    def __new__(cls, path="config.yaml"):
        abs_path = os.path.abspath(path)
        if abs_path not in cls._cache:
            instance = super().__new__(cls)
            instance._read(abs_path)
            cls._cache[abs_path] = instance
        return cls._cache[abs_path]

    def _read(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ValueError("Root config must be a dictionary")
            self._config = data

    def get(self, section, default=None):
        return self._config.get(section, default)

    @property
    def full(self):
        return self._config

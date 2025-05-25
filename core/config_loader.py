import os
import yaml

class ConfigLoader:
    _singleton_instance = None
    _singleton_path = None

    def __new__(cls, path="config.yaml"):
        abs_path = os.path.abspath(path)

        if cls._singleton_instance is None:
            instance = super().__new__(cls)
            instance._load(abs_path)
            cls._singleton_instance = instance
            cls._singleton_path = abs_path
        elif abs_path != cls._singleton_path:
            raise RuntimeError(
                f"ConfigLoader was already initialized with a different path: '{cls._singleton_path}'. "
                f"Refusing to load another config from: '{abs_path}'"
            )

        return cls._singleton_instance

    def _load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Configuration must be a dictionary at root level")
            self._config = config
            self._path = path

    def get(self, section, default=None):
        return self._config.get(section, default)

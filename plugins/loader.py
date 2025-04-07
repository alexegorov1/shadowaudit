import os
import sys
import importlib.util
from types import ModuleType
from typing import List, Dict, Type
from core.interfaces import BaseCollector, BaseAnalyzer, BaseReporter
from core.logger import LoggerFactory
from core.config_loader import ConfigLoader

logger = LoggerFactory(ConfigLoader().get("general", {})).create_logger("shadowaudit.plugins.loader")

def _load_module_from_path(module_name: str, file_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def discover_plugins(directory: str = "plugins") -> Dict[str, List]:
    plugin_registry = {"collectors": [], "analyzers": [], "reporters": []}
    directory_path = os.path.abspath(directory)

    if not os.path.exists(directory_path):
        logger.info(f"Plugin directory does not exist: {directory_path}")
        return plugin_registry

    sys.path.insert(0, directory_path)

    for filename in os.listdir(directory_path):
        if not filename.endswith(".py") or filename == "__init__.py" or filename == "loader.py":
            continue

        module_name = filename[:-3]
        file_path = os.path.join(directory_path, filename)

        try:
            module = _load_module_from_path(module_name, file_path)

            for attr_name in dir(module):
                obj = getattr(module, attr_name)
                if isinstance(obj, type):
                    if issubclass(obj, BaseCollector) and obj is not BaseCollector:
                        plugin_registry["collectors"].append(obj())
                        logger.debug(f"Registered plugin collector: {obj.__name__}")
                    elif issubclass(obj, BaseAnalyzer) and obj is not BaseAnalyzer:
                        plugin_registry["analyzers"].append(obj())
                        logger.debug(f"Registered plugin analyzer: {obj.__name__}")
                    elif issubclass(obj, BaseReporter) and obj is not BaseReporter:
                        plugin_registry["reporters"].append(obj())
                        logger.debug(f"Registered plugin reporter: {obj.__name__}")

        except Exception as e:
            logger.warning(f"Failed to load plugin '{filename}': {e}")

    sys.path.pop(0)
    return plugin_registry

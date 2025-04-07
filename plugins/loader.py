import os
import sys
import importlib.util
from types import ModuleType
from typing import List, Dict, Type
from core.interfaces import BaseCollector, BaseAnalyzer, BaseReporter
from core.logger import LoggerFactory
from core.config_loader import ConfigLoader

logger = LoggerFactory(ConfigLoader().get("general", {})).create_logger("shadowaudit.plugins.loader")


def _load_python_module(module_name: str, file_path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Failed to load spec from {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_valid_plugin_class(obj: Type, base_cls: Type) -> bool:
    return isinstance(obj, type) and issubclass(obj, base_cls) and obj is not base_cls


def _register_plugins_from_module(module: ModuleType, registry: Dict[str, List]) -> None:
    for attr_name in dir(module):
        obj = getattr(module, attr_name)
        if _is_valid_plugin_class(obj, BaseCollector):
            instance = obj()
            name = getattr(instance, "get_name", lambda: "unknown")()
            registry["collectors"].append(instance)
            logger.info(f"Loaded plugin collector: {name}")
        elif _is_valid_plugin_class(obj, BaseAnalyzer):
            instance = obj()
            name = getattr(instance, "get_name", lambda: "unknown")()
            registry["analyzers"].append(instance)
            logger.info(f"Loaded plugin analyzer: {name}")
        elif _is_valid_plugin_class(obj, BaseReporter):
            instance = obj()
            name = getattr(instance, "get_name", lambda: "unknown")()
            registry["reporters"].append(instance)
            logger.info(f"Loaded plugin reporter: {name}")


def discover_plugins(directory: str = "plugins") -> Dict[str, List]:
    plugin_registry = {"collectors": [], "analyzers": [], "reporters": []}
    directory_path = os.path.abspath(directory)

    if not os.path.isdir(directory_path):
        logger.debug(f"No plugin directory found at: {directory_path}")
        return plugin_registry

    sys.path.insert(0, directory_path)

    for filename in sorted(os.listdir(directory_path)):
        if not filename.endswith(".py"):
            continue
        if filename in {"__init__.py", "loader.py"}:
            continue

        module_name = filename[:-3]
        file_path = os.path.join(directory_path, filename)

        try:
            module = _load_python_module(module_name, file_path)
            _register_plugins_from_module(module, plugin_registry)
        except Exception as e:
            logger.warning(f"Error loading plugin module '{filename}': {e}")

    sys.path.pop(0)
    return plugin_registry

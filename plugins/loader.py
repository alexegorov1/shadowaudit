import os
import sys
import importlib.util
from types import ModuleType
from typing import Dict, List, Type
from core.interfaces import BaseCollector, BaseAnalyzer, BaseReporter
from core.logger import LoggerFactory
from core.config_loader import ConfigLoader

logger = LoggerFactory(ConfigLoader().get("general", {})).create_logger("shadowaudit.plugins.loader")


def _load_module(name: str, path: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load spec for: {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_subclass(obj, base: Type) -> bool:
    return isinstance(obj, type) and issubclass(obj, base) and obj is not base


def _collect_plugin_classes(module: ModuleType) -> Dict[str, List]:
    found = {"collectors": [], "analyzers": [], "reporters": []}

    for attr in dir(module):
        obj = getattr(module, attr)
        if _is_subclass(obj, BaseCollector):
            found["collectors"].append(obj)
        elif _is_subclass(obj, BaseAnalyzer):
            found["analyzers"].append(obj)
        elif _is_subclass(obj, BaseReporter):
            found["reporters"].append(obj)

    return found


def discover_plugins(directory: str = "plugins") -> Dict[str, List]:
    plugins: Dict[str, List] = {"collectors": [], "analyzers": [], "reporters": []}
    seen_names = set()
    plugin_dir = os.path.abspath(directory)

    if not os.path.isdir(plugin_dir):
        logger.debug(f"Plugin directory does not exist: {plugin_dir}")
        return plugins

    sys.path.insert(0, plugin_dir)

    for filename in sorted(os.listdir(plugin_dir)):
        if not filename.endswith(".py") or filename in {"__init__.py", "loader.py"}:
            continue

        module_name = filename[:-3]
        module_path = os.path.join(plugin_dir, filename)

        try:
            module = _load_module(module_name, module_path)
            plugin_classes = _collect_plugin_classes(module)

            for category, classes in plugin_classes.items():
                for cls in classes:
                    try:
                        instance = cls()
                        name = getattr(instance, "get_name", lambda: cls.__name__)()
                        if name in seen_names:
                            raise ValueError(f"Duplicate plugin name: {name}")
                        seen_names.add(name)
                        plugins[category].append(instance)
                        logger.info(f"Loaded plugin [{category}] → {name}")
                    except Exception as inst_err:
                        logger.warning(f"Failed to instantiate {cls.__name__}: {inst_err}")

        except Exception as mod_err:
            logger.warning(f"Failed to load plugin module '{filename}': {mod_err}")

    sys.path.pop(0)
    return plugins

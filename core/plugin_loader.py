import os
import importlib.util
import inspect
from typing import List, Type
from core.interfaces import BaseCollector

def discover_collectors(directory="collector") -> List[BaseCollector]:
    collectors = []
    seen_names = set()
    base_path = os.path.abspath(directory)

    if not os.path.isdir(base_path):
        return collectors

    for filename in os.listdir(base_path):
        if not filename.endswith(".py") or filename.startswith("_") or filename == "__init__.py":
            continue

        try:
            spec = importlib.util.spec_from_file_location(f"{directory}.{module_name}", module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseCollector) and obj is not BaseCollector:
                        instance = obj()
                        name = instance.get_name()
                        seen_names.add(name)
                        collectors.append(instance)
        except Exception as e:
            print(f"[plugin_loader] Failed to load module '{module_name}': {e}")

    return collectors

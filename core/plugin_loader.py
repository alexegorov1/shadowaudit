import importlib
import pkgutil

def discover_plugins(package, base_class):
    implementations = []

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, base_class) and attr is not base_class:
                implementations.append(attr)

    return implementations

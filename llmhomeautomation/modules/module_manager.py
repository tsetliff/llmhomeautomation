import importlib
import pkgutil
from llmhomeautomation.modules.module import Module

class ModuleManager:
    _instance = None  # Class-level attribute for the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModuleManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'modules'):
            self.modules = self.load_modules()

    def load_modules(self):
        modules = {}  # Use a dict for easy access to modules by name
        package = 'llmhomeautomation.modules'

        # Discover all submodules in the modules directory
        for finder, name, ispkg in pkgutil.iter_modules(['llmhomeautomation/modules']):
            if ispkg:
                try:
                    # Dynamically import the module
                    module_path = f"{package}.{name}.{name}"
                    module_lib = importlib.import_module(module_path)

                    # Get the class with the same name as the module (Capitalized)
                    class_name = name.capitalize()
                    module_class = getattr(module_lib, class_name)

                    # Instantiate and store the module if it's enabled
                    if issubclass(module_class, Module):
                        init_module = module_class()
                        if init_module.enabled():
                            modules[name] = init_module  # Store instance by module name
                        print(f"Loaded module: {class_name}")
                except (ImportError, AttributeError) as e:
                    print(f"Failed to load {name}: {e}")

        return modules  # Return dictionary of persistent modules

    def process_request(self, status: dict) -> dict:
        # Pass status through each persistent module
        for module_name, module in self.modules.items():
            status = module.process_request(status)
        return status

    def process_status(self, status: dict) -> dict:
        # Pass status through each persistent module
        for module_name, module in self.modules.items():
            status = module.process_status(status)
            print(f"{module_name} updated status: {status}")
        return status


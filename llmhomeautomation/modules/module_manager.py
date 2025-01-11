import importlib
import json
import os
import sys
from llmhomeautomation.modules.module import Module

class ModuleManager:
    _instance = None  # Singleton instance
    CONFIG_FILE = 'modules.json'  # Path to the JSON file

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModuleManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'modules'):
            self.modules = {}
            self.load_modules()

    def load_modules(self):
        """Load enabled modules based on the JSON config."""
        if not os.path.exists(self.CONFIG_FILE):
            print(f"Config file {self.CONFIG_FILE} not found. Creating a new one.")
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump({}, file)

        with open(self.CONFIG_FILE, 'r') as file:
            config = json.load(file)

        for module_name, is_enabled in config.items():
            if is_enabled:
                print(f"Loading module {module_name}")
                self._load_module(module_name)
            else:
                print(f"Skipping module {module_name} as it is disabled.")

    def _load_module(self, module_name):
        """Dynamically load a single module by its name."""
        try:
            module_path = f"llmhomeautomation.modules.{module_name}.{module_name.split('.')[-1]}"
            module_lib = importlib.import_module(module_path)

            # Extract the class name from the module name
            class_name = module_name.split('.')[-1].capitalize()
            module_class = getattr(module_lib, class_name)

            if issubclass(module_class, Module):
                self.modules[module_name] = module_class()
        except (ImportError, AttributeError) as e:
            print(f"Failed to load {module_name}: {e}")

    def enable_module(self, module_name):
        """Enable a module in memory and the JSON config."""
        with open(self.CONFIG_FILE, 'r') as file:
            config = json.load(file)

        if not config.get(module_name, False):
            config[module_name] = True
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(config, file, indent=4)

            self._load_module(module_name)
            print(f"Module '{module_name}' has been enabled.")

    def disable_module(self, module_name):
        """Disable a module in memory and the JSON config."""
        with open(self.CONFIG_FILE, 'r') as file:
            config = json.load(file)

        if config.get(module_name, False):
            config[module_name] = False
            with open(self.CONFIG_FILE, 'w') as file:
                json.dump(config, file, indent=4)

            if module_name in self.modules:
                del self.modules[module_name]
                print(f"Module '{module_name}' has been disabled.")

    def process_whoami(self, whoami: list) -> list:
        # Pass status through each persistent module
        for module in self.modules.values():
            whoami = module.process_whoami(whoami)
        return whoami

    def process_request(self, status: dict) -> dict:
        # Pass status through each persistent module
        for module in self.modules.values():
            status = module.process_request(status)
        return status

    def process_status(self, status: dict) -> dict:
        # Pass status through each persistent module
        for module in self.modules.values():
            status = module.process_status(status)
        return status

    def process_command_examples(self, command_examples: list) -> list:
        # Pass status through each persistent module
        for module in self.modules.values():
            command_examples = module.process_command_examples(command_examples)
        return command_examples


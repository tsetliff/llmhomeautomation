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
        module_path = f"llmhomeautomation.modules.{module_name}.{module_name.split('.')[-1]}"
        module_lib = importlib.import_module(module_path)

        # Fix: Convert snake_case to PascalCase
        raw_class_name = module_name.split('.')[-1]  # 'google_text_to_speech'
        class_name = ''.join(part.capitalize() for part in raw_class_name.split('_'))  # 'GoogleTextToSpeech'

        module_class = getattr(module_lib, class_name)

        if issubclass(module_class, Module):
            self.modules[module_name] = module_class()

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

    def return_first(func):
        def wrapper(self, data):
            for module in self.modules.values():
                print(f"Trying module: {module.__class__.__name__}")
                method = getattr(module, func.__name__, None)
                if method:
                    result = method(data)
                    if result is not None:
                        return result
            return None
        return wrapper

    def with_ownership(func):
        def wrapper(self, data):
            return self._process_with_ownership(data, func.__name__)

        return wrapper

    @with_ownership
    def process_history(self, history: list) -> list:
        pass

    @return_first
    def llm_request(self, messages: list) -> str | None:
        pass

    @with_ownership
    def process_whoami(self, whoami: list) -> list:
        pass

    @with_ownership
    def process_status(self, status: dict) -> dict:
        pass

    @with_ownership
    def process_command_examples(self, command_examples: list) -> list:
        pass

    @with_ownership
    def process_request(self, request: dict) -> dict:
        pass

    @with_ownership
    def process_response(self, response: dict) -> dict:
        pass

    @with_ownership
    def process_commands(self, commands: list) -> list:
        pass

    def _process_with_ownership(self, data, method_name: str):
        owned_items = set()

        for module in self.modules.values():
            module_owns = module.owns()

            # Skip the module if it owns already claimed items
            if any(item in owned_items for item in module_owns):
                print(f"Skipping {module.__class__.__name__} when calling {method_name} because it is trying to own already claimed items: {module_owns}")
                continue

            # Update the owned items
            owned_items.update(module_owns)

            # Dynamically call the module's method
            method = getattr(module, method_name, None)
            if method:
                data = method(data)
                # Module has handled something completely and doesn't want to continue.
                if data is None:
                    break
            else:
                print(f"Module {module} does not have a method '{method_name}'")

        return data

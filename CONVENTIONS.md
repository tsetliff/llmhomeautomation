# Project Conventions

## Module Structure

- All functionality should be organized into modules located in `./llmhomeautomation/modules`.
- Each module should ideally be first within a category directory like listen and then in a directory of the same name.
- Each module must reside in its own sub directory of the same name as the main module file such as llmhomeautomation/modules/listen/vosk/vosk.
- Each module that requires system constants needs to load from dotenv import load_dotenv and load_dotenv() before doing any work.
- Requests to modules and from modules to modules should go through the module manager ModuleManager().llm_request(messages)

## Module Components
- Each module directory should contain a `description.txt` file that concisely explains the module's purpose and functionality.
- Modules should include Python tests to ensure functionality and reliability.
# Project Conventions

## Module Structure

- All functionality should be organized into modules located in `./llmhomeautomation/modules`.
- Each module must reside in its own directory.

## Module Components

- Each module directory should contain a `description.txt` file that concisely explains the module's purpose and functionality.
- Modules should include Python tests to ensure functionality and reliability.

## Core Files

- Core files that orchestrate the modules should not be placed within the module directories.
- These core files are responsible for managing and integrating the modules into the system.

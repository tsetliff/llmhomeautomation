#!/bin/bash

# Get the directory where the script is located
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Change to the script's directory if not already there
if [ "$PWD" != "$script_dir" ]; then
  echo "Switching to the script directory."
  cd "$script_dir" || exit
fi

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Not in a virtual environment. Activating..."
  source venv/bin/activate
fi

python3 -m llmhomeautomation.main

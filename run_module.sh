#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <module_name>"
  exit 1
fi

# Make sure setup was run
if [[ ! -f ".env" ]]; then
  echo "Error: .env file not found. Please run setup.sh first."
  exit 1
fi

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

python3 -m $1

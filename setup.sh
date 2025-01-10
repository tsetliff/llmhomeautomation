#!/bin/bash
set -e

# Path to the .env file
ENV_FILE=".env"
DATA_DIR="./data"
GOOGLE_CLOUD_KEY_DIR="$HOME/.config/gcloud/"
GOOGLE_CLOUD_KEY_FILE="application_default_credentials.json"


# Function to prompt the user for yes or no
prompt_yes_no() {
  local prompt="$1"
  local response
  while true; do
    read -p "$prompt [y/n]: " response
    case "${response,,}" in  # Convert to lowercase
      y*) return 0 ;;         # Return 0 for "yes"
      n*) return 1 ;;         # Return 1 for "no"
      *) echo "Invalid input. Please enter y or n." ;;
    esac
  done
}


# Ensure the data directory exists
mkdir -p "$DATA_DIR"

# Ensure the google cloud key directory exists
mkdir -p "$GOOGLE_CLOUD_KEY_DIR"

# Check if /etc/os-release exists
if [ ! -f /etc/os-release ]; then
  echo "Error: /etc/os-release not found. Unable to determine the operating system."
  exit 1
fi

# Source the OS information
. /etc/os-release

# Ensure it's Ubuntu
if [ "$ID" != "ubuntu" ]; then
  echo "Error: This script is only tested on Ubuntu. Detected OS: $NAME"
  exit 1
fi

# Parse the Ubuntu version
UBUNTU_VERSION=${VERSION_ID}

# Check if the version is at least 24.4
if [[ "$(echo "$UBUNTU_VERSION >= 24.01" | bc)" -eq 0 ]]; then
  echo "Error: This script is only tested on Ubuntu 24.4 and higher. Detected version: $UBUNTU_VERSION"
  exit 1
fi

# Install ubuntu packages
sudo apt update
sudo apt install -y python3-pip python3-venv zip unzip apt-transport-https ca-certificates gnupg curl \
     libportaudio2 libportaudiocpp0 portaudio19-dev alsa-utils supervisor

# Get the directory where the script is located
script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Change to the script's directory if not already there
if [ "$PWD" != "$script_dir" ]; then
  echo "Switching to the script directory."
  cd "$script_dir" || exit
fi

# Make sure the google cloud key has been placed in the correct directory.
if [ ! -f "$GOOGLE_CLOUD_KEY_DIR$GOOGLE_CLOUD_KEY_FILE" ]; then
  echo "Error: copy your google cloud credentials file to $GOOGLE_CLOUD_KEY_DIR$GOOGLE_CLOUD_KEY_FILE."
  exit 1
fi

python3 -m venv venv

# Check if in a virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
  echo "Already in a virtual environment: $VIRTUAL_ENV"
  read -p "Do you want to continue in this environment? Press Enter to continue or Ctrl+C to exit... "
else
  echo "Not in a virtual environment. Activating..."
  source venv/bin/activate
fi

pip install -r requirements.txt

# Ensure the data directory exists
mkdir -p "$DATA_DIR"

if [ ! -f "$ENV_FILE" ]; then
  echo "$ENV_FILE file not found, creating one."
  touch $ENV_FILE
fi

# Check if AI_NAME exists in the .env file and has a value
AI_NAME=$(grep -E '^AI_NAME=' "$ENV_FILE" | cut -d '=' -f2)

if [ -z "$AI_NAME" ]; then
  # Prompt the user for the AI_NAME value
  echo ""
  read -p "What would you to name your AI, this is your wake word. You may enter multiple comma seperated words without spaces: " USER_KEY

  # Ensure the input is not empty
  if [ -z "$USER_KEY" ]; then
    echo "You didn't give me a value, Tom it is..."
    USER_KEY="Tom"
  fi

  # If AI_NAME exists as a blank line, replace it; otherwise, append it
  if grep -q '^AI_NAME=' "$ENV_FILE"; then
    sed -i "s|^AI_NAME=.*|AI_NAME=$USER_KEY|" "$ENV_FILE"
  else
    echo "AI_NAME=$USER_KEY" >> "$ENV_FILE"
  fi

  echo "AI_NAME is now $USER_KEY"
else
  echo "AI_NAME is already set in $ENV_FILE with a value $AI_NAME."
fi

# Check if OPENAI_KEY exists in the .env file and has a value
OPENAI_KEY=$(grep -E '^OPENAI_KEY=' "$ENV_FILE" | cut -d '=' -f2)

if [ -z "$OPENAI_KEY" ]; then
  # Prompt the user for the OPENAI_KEY value
  read -p "Enter your OpenAI API key: " USER_KEY

  # Ensure the input is not empty
  if [ -z "$USER_KEY" ]; then
    echo "Error: OpenAI API key cannot be empty."
    exit 1
  fi

  # If OPENAI_KEY exists as a blank line, replace it; otherwise, append it
  if grep -q '^OPENAI_KEY=' "$ENV_FILE"; then
    sed -i "s|^OPENAI_KEY=.*|OPENAI_KEY=$USER_KEY|" "$ENV_FILE"
  else
    echo "OPENAI_KEY=$USER_KEY" >> "$ENV_FILE"
  fi

  echo "OpenAI API key saved to $ENV_FILE."
else
  echo "OPENAI_KEY is already set in $ENV_FILE with a value."
fi

# Check if VOSK_MODEL is already set in .env
VOSK_MODEL=$(grep -E '^VOSK_MODEL=' "$ENV_FILE" | cut -d '=' -f2)

if [ -z "$VOSK_MODEL" ]; then
  echo "VOSK_MODEL is not set. Checking system memory..."

  # Check total memory in GB
  TOTAL_MEM_GB=$(free -g | awk '/^Mem:/{print $2}')

  # Determine the appropriate model based on memory
  if [ "$TOTAL_MEM_GB" -ge 15 ]; then
    MODEL="vosk-model-en-us-0.22"
    MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
  else
    MODEL="vosk-model-small-en-us-0.15"
    MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
  fi

  # Append or update VOSK_MODEL in .env
  if grep -q '^VOSK_MODEL=' "$ENV_FILE"; then
    sed -i "s|^VOSK_MODEL=.*|VOSK_MODEL=$MODEL|" "$ENV_FILE"
  else
    echo "VOSK_MODEL=$MODEL" >> "$ENV_FILE"
  fi

  echo "VOSK_MODEL set to $MODEL in $ENV_FILE."
else
  echo "VOSK_MODEL is already set in .env with the value: $VOSK_MODEL"
  MODEL="$VOSK_MODEL"
  if [ "$MODEL" = "vosk-model-en-us-0.22" ]; then
    MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip"
  elif [ "$MODEL" = "vosk-model-small-en-us-0.15" ]; then
    MODEL_URL="https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
  else
    echo "Unknown model: $MODEL. Exiting."
    exit 1
  fi
fi


# Make sure there is an audio device that can play back
# Get the current PLAYBACK_DEVICE from the .env file
if [ -f "$ENV_FILE" ]; then
  PLAYBACK_DEVICE=$(grep -E '^PLAYBACK_DEVICE=' "$ENV_FILE" | cut -d '=' -f2-)
else
  touch "$ENV_FILE"
  PLAYBACK_DEVICE=""
fi

# Ask if they want to update the PLAYBACK_DEVICE if it is set
if [ -n "$PLAYBACK_DEVICE" ]; then
  echo "Current PLAYBACK_DEVICE is: $PLAYBACK_DEVICE"
  if prompt_yes_no "Would you like to update it?"; then
    PLAYBACK_DEVICE=""
  fi
fi

if [ -z "$PLAYBACK_DEVICE" ]; then
  devices=($(aplay -L | grep -v '^ '))

  # Loop through devices to test
  for device in "${devices[@]}"; do
    echo "Testing device: $device"
    aplay -D "$device" ./library/test.wav 2>/dev/null

    read -p "Did you hear the sound? (Enter for no, y for yes): " response
    if [[ "${response,,}" =~ ^y ]]; then
      # Update the PLAYBACK_DEVICE in .env
      if grep -q '^PLAYBACK_DEVICE=' "$ENV_FILE"; then
        sed -i "s|^PLAYBACK_DEVICE=.*|PLAYBACK_DEVICE=$device|" "$ENV_FILE"
      else
        echo "PLAYBACK_DEVICE=$device" >> "$ENV_FILE"
      fi
      PLAYBACK_DEVICE="$device"
      echo "PLAYBACK_DEVICE set to: $device"
      break
    fi
  done
fi

if [ -z "$PLAYBACK_DEVICE" ]; then
  echo "Make sure your speakers are connected and your volume is up and run setup again."
  exit 1
fi

if grep -q '^PLAYBACK_DEVICE=' "$ENV_FILE"; then
  sed -i "s|^PLAYBACK_DEVICE=.*|PLAYBACK_DEVICE=$PLAYBACK_DEVICE|" "$ENV_FILE"
else
  echo "PLAYBACK_DEVICE=$PLAYBACK_DEVICE" >> "$PLAYBACK_DEVICE"
fi

# Make sure there is an audio device that can play back
# Get the current RECORD_DEVICE from the .env file
if [ -f "$ENV_FILE" ]; then
  RECORD_DEVICE=$(grep -E '^RECORD_DEVICE=' "$ENV_FILE" | cut -d '=' -f2-)
else
  touch "$ENV_FILE"
  RECORD_DEVICE=""
fi

# Ask if they want to update the RECORD_DEVICE if it is set
arecord -l
if [ -n "$RECORD_DEVICE" ]; then
  echo "Current RECORD_DEVICE is: $RECORD_DEVICE, use the Card number, if there's more then one subdevice you can use 1,0 where 1 is the card number and 0 is the sub device."
  if prompt_yes_no "Would you like to update it?"; then
    read -p "Enter a device number: " RECORD_DEVICE
  fi
else
  read -p "Enter a device number: " RECORD_DEVICE
fi

if [ -z "$RECORD_DEVICE" ]; then
  echo "You must enter a numeric recording device id."
  exit 1
fi

echo "Setting it to $RECORD_DEVICE"

if grep -q '^RECORD_DEVICE=' "$ENV_FILE"; then
  sed -i "s|^RECORD_DEVICE=.*|RECORD_DEVICE=$RECORD_DEVICE|" "$ENV_FILE"
else
  echo "RECORD_DEVICE=$RECORD_DEVICE" >> "$ENV_FILE"
fi

# Check if the model directory exists
MODEL_DIR="$DATA_DIR/$MODEL"
if [ ! -d "$MODEL_DIR" ]; then
  echo "Model directory $MODEL_DIR not found. Downloading the model..."

  # Download the model
  ZIP_FILE="$DATA_DIR/$MODEL.zip"
  curl -o "$ZIP_FILE" -L "$MODEL_URL"

  # Extract the model
  echo "Extracting the model..."
  unzip "$ZIP_FILE" -d "$DATA_DIR"

  # Clean up the zip file
  rm "$ZIP_FILE"

  echo "Model downloaded and extracted to $MODEL_DIR."
else
  echo "Model directory $MODEL_DIR already exists. Skipping download."
fi

# Make sure this is executable before supervisor is set up to run it
chmod 700 run_module.sh

sudo systemctl start supervisor
sudo systemctl enable supervisor

SUPERVISOR_DIR="/etc/supervisor/conf.d"
SOURCE_DIR="./supervisor"
WORKING_DIR=$(pwd)  # Get the current working directory

# Check if SOURCE_DIR exists
if [ ! -d "$SOURCE_DIR" ]; then
  echo "Error: Source directory '$SOURCE_DIR' does not exist."
  exit 1
fi

# Ensure Supervisor directory exists
if [ ! -d "$SUPERVISOR_DIR" ]; then
  echo "Error: Supervisor directory '$SUPERVISOR_DIR' does not exist."
  exit 1
fi

# Process each .conf file in the SOURCE_DIR
for CONF_FILE in "$SOURCE_DIR"/*.conf; do
  if [ -f "$CONF_FILE" ]; then
    # Replace PATH with the actual working directory
    sudo sed "s|PATH|$WORKING_DIR|g; s|USER|$USER|g" "$CONF_FILE" > "/tmp/$(basename "$CONF_FILE")"
    sudo mv "/tmp/$(basename "$CONF_FILE")" "$SUPERVISOR_DIR/$(basename "$CONF_FILE")"
    echo "Copied and updated: $(basename "$CONF_FILE")"
  else
    echo "No .conf files found in $SOURCE_DIR"
  fi
done

# Reload Supervisor to apply any configuration changes
sudo systemctl restart supervisor
sleep 3

echo "Supervisor setup complete!"
sudo supervisorctl status
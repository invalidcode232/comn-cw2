#!/bin/bash

# Check if script number is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <script_number>"
  echo "Example: $0 1"
  exit 1
fi

SCRIPT_NUM=$1

# Execute the corresponding receiver script
echo "Starting Receiver${SCRIPT_NUM}..."
python3 "Receiver${SCRIPT_NUM}.py" 54321 "r${SCRIPT_NUM}file.jpg"

#!/bin/bash

# Check if script number is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <script_number> [retry_timeout] [window_size]"
  echo "Examples:"
  echo "  $0 1"
  echo "  $0 2 500"
  echo "  $0 3 500 1024"
  exit 1
fi

SCRIPT_NUM=$1
TIMEOUT=$2
WINDOW=$3

case $SCRIPT_NUM in
1)
  echo "Starting Sender1..."
  python3 Sender1.py localhost 54321 test.jpg
  ;;
2)
  if [ -z "$TIMEOUT" ]; then
    echo "Error: Sender 2 requires a <retry_timeout> argument."
    echo "Usage: $0 2 <retry_timeout>"
    exit 1
  fi
  echo "Starting Sender2 with timeout: $TIMEOUT..."
  python3 Sender2.py localhost 54321 test.jpg "$TIMEOUT"
  ;;
3 | 4)
  if [ -z "$TIMEOUT" ] || [ -z "$WINDOW" ]; then
    echo "Error: Sender $SCRIPT_NUM requires both <retry_timeout> and <window_size> arguments."
    echo "Usage: $0 $SCRIPT_NUM <retry_timeout> <window_size>"
    exit 1
  fi
  echo "Starting Sender${SCRIPT_NUM} with timeout: $TIMEOUT and window size: $WINDOW..."
  python3 "Sender${SCRIPT_NUM}.py" localhost 54321 test.jpg "$TIMEOUT" "$WINDOW"
  ;;
*)
  echo "Error: Invalid script number. Please choose 1, 2, 3, or 4."
  exit 1
  ;;
esac

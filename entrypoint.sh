#!/bin/sh
stty -echoctl < /dev/tty 2>/dev/null || true
SIZE_FILE="/tmp/clock-size-$$"
CMD_FILE="/tmp/clock-cmd-$$"
export CLOCK_SIZE_FILE="$SIZE_FILE"
export CLOCK_CMD_FILE="$CMD_FILE"
: > "$CMD_FILE"
(while :; do stty size < /dev/tty > "$SIZE_FILE" 2>/dev/null; sleep 0.25; done) &
SIZE_PID=$!
(trap '' INT; while IFS= read -r line; do printf '%s\n' "$line" >> "$CMD_FILE"; done) &
READER_PID=$!
trap 'kill "$SIZE_PID" "$READER_PID" 2>/dev/null; rm -f "$SIZE_FILE" "$CMD_FILE"' EXIT TERM
set -- $(stty size < /dev/tty)
export LINES=$1
export COLUMNS=$2
python3 main.py

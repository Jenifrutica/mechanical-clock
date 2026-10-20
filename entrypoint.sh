#!/bin/sh
stty -echoctl 2>/dev/null || true
SIZE_FILE="/tmp/clock-size-$$"
export CLOCK_SIZE_FILE="$SIZE_FILE"
(while :; do stty size > "$SIZE_FILE" 2>/dev/null; sleep 1; done) &
LOOP_PID=$!
trap 'kill "$LOOP_PID" 2>/dev/null; rm -f "$SIZE_FILE"' EXIT INT TERM
set -- $(stty size)
export LINES=$1
export COLUMNS=$2
python3 main.py

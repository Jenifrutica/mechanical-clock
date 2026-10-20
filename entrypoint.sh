#!/bin/sh
stty -echoctl < /dev/tty 2>/dev/null || true
SIZE_FILE="/tmp/clock-size-$$"
CMD_FILE="/tmp/clock-cmd-$$"
export CLOCK_SIZE_FILE="$SIZE_FILE"
export CLOCK_CMD_FILE="$CMD_FILE"
: > "$CMD_FILE"
(while :; do stty size < /dev/tty > "$SIZE_FILE" 2>/dev/null; sleep 0.25; done) &
SIZE_PID=$!
setsid python3 main.py < /dev/null &
APP_PID=$!
(while kill -0 "$APP_PID" 2>/dev/null; do sleep 1; done; kill -TERM $$) &
WATCH_PID=$!
trap 'printf "__menu__\n" >> "$CMD_FILE"' INT
trap 'kill "$SIZE_PID" "$WATCH_PID" 2>/dev/null; rm -f "$SIZE_FILE" "$CMD_FILE"' EXIT TERM
while :; do
    if IFS= read -r line; then
        printf '%s\n' "$line" >> "$CMD_FILE"
    fi
done

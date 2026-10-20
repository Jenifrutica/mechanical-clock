#!/bin/sh
stty -echoctl 2>/dev/null || true
set -- $(stty size)
export LINES=$1
export COLUMNS=$2
exec python3 main.py

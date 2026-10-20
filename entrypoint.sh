#!/bin/sh
set -- $(stty size)
export LINES=$1
export COLUMNS=$2
exec python3 main.py

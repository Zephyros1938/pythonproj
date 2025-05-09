#!/bin/bash
set -e  # Exit on error

clear

if [ "$COLUMNS" -gt 260 ]; then
    cat .logohuge
elif [ "$COLUMNS" -gt 170 ]; then
    cat .logobig
else
    cat .logo
fi

./.venv/bin/python main.py

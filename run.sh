#!/bin/bash
set -e  # Exit on error

clear

cat .logo
echo $COLUMNS

./.venv/bin/python main.py

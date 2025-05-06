#!/bin/bash
set -e  # Exit on error

clear

cat .logo

./.venv/bin/python main.py

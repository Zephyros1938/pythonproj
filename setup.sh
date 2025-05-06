#!/bin/bash
set -e  # Exit on error

clear
echo "Installing dependencies..."

# Check for venv existence
if [ ! -f "./.venv/bin/pip" ]; then
    echo "Virtual environment not found."

    read -p "Would you like to create one now? (y/n): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "Creating virtual environment in .venv..."
        mkdir -p .venv
        python -m venv .venv
    else
        echo "Aborting setup. Please create the virtual environment manually."
        exit 1
    fi
fi

# Install dependencies
echo "Installing dependencies..."
./.venv/bin/pip install --disable-pip-version-check -r requirements.txt > /dev/null 2>&1
echo "Successfully installed, you can run by using ./run.sh"

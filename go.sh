#!/bin/bash

# --- Configuration ---
VENV_DIR="cm-venv"
START_SCRIPT="src.codemerger"
SPEC_FILE="codemerger.spec"
FLAG=$1

# --- Environment Setup ---
# Check if the virtual environment is already active
if [ -z "$VIRTUAL_ENV" ]; then
    # Check if the virtual environment directory exists
    if [ ! -d "$VENV_DIR/bin" ]; then
        echo "Virtual environment not found. Creating a new one..."
        python3 -m venv $VENV_DIR

        # Activate the virtual environment
        source $VENV_DIR/bin/activate

        # Install required packages from requirements.txt
        if [ -f "requirements.txt" ]; then
            echo "Installing required packages..."
            pip install -r requirements.txt
        else
            echo "requirements.txt not found. Skipping package installation."
        fi
    else
        # Activate the virtual environment if it already exists
        echo "Activating virtual environment..."
        source $VENV_DIR/bin/activate
    fi
fi

# --- Command Handling ---

# Update requirements.txt
if [ "$FLAG" == "f" ]; then
    echo ""
    echo "--- Writing requirements.txt ---"
    pip freeze > requirements.txt
    echo "Done."
    exit 0
fi

# Check for the 'build' flag
if [ "$FLAG" == "b" ]; then
    echo ""
    echo "--- Starting PyInstaller Build ---"
    echo "Deleting old build folders..."
    rm -rf dist build
    echo "Running PyInstaller with $SPEC_FILE..."
    pyinstaller $SPEC_FILE
    echo ""
    echo "--- Build Complete! ---"
    echo "Application is located in the 'dist' folder."
    exit 0
fi

# --- Default Action: Run the Python Script ---
echo "Starting CodeMerger application..."
python3 -m $START_SCRIPT
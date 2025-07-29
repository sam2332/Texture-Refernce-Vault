#!/bin/bash
# Collection Import Tool for Unix/Linux
# This script makes it easier to run the import tool on Unix/Linux systems

echo "================================================="
echo "Texture Reference Vault - Collection Import Tool"
echo "================================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python is not installed or not in PATH"
        echo "Please install Python and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "Usage: ./import_collection.sh [options]"
    echo ""
    echo "Examples:"
    echo "  ./import_collection.sh --list-users"
    echo "  ./import_collection.sh --folder \"/path/to/textures\" --name \"Texture Pack\" --owner admin_1"
    echo ""
    echo "For full help:"
    $PYTHON_CMD import_collection.py --help
    exit 0
fi

# Run the Python script with all arguments
$PYTHON_CMD import_collection.py "$@"

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo "Import completed!"
else
    echo ""
    echo "Import failed! Check the error messages above."
    exit 1
fi

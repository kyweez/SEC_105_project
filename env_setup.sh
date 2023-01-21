#!/bin/bash

echo "======================== DEACTIVATE ENVIRONMENT ========================"
echo ""

# Check if currently in a virtual environment
if [[ -n "$VIRTUAL_ENV" ]]; then
    echo "Deactivating current virtual environment..."
    deactivate
else
    echo "Not currently in a virtual environment..."
fi

echo ""
echo "======================= REMOVING OLD ENVIRONMENT ======================="
echo ""

# Check if virtual environment already exists in current folder
if [ -d "venv" ]; then
    echo "Removing existing virtual environment..."
    rm -rf venv
else
    echo "No existing virtual environment found..."
fi

# Create and activate new virtual environment
echo "Creating new virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "=========================== INSTALL DEV TOOLS =========================="
echo ""

# Install required packages
echo "Installing required packages..."
pip3 install -r requirements-dev.txt

echo ""
echo "========================== INSTALL TESTS TOOLS ========================="
echo ""

# Install required packages for tests
echo "Installing required packages for tests..."
pip3 install -r tests/requirements-test.txt

echo ""
echo "============================ INSTALL PROJECT ==========================="
echo ""

# Install the package in editable mode
echo "Installing package in editable mode..."
pip3 install -e .

echo ""
echo "======================== STUBS PACKAGES INSTALL ========================"
echo ""

# Install missing library stubs
echo "Installing missing library stubs..."
source handle_mypy_missing_library_stubs.sh

echo ""
echo "========================= INSTALLING PRE-COMMIT ========================"
echo ""

# Install pre-commit
echo "Installing pre-commit..."
pre-commit install

#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCR_WRAP_PATH="$SCRIPT_DIR/scr-wrap"

# Ensure ~/.local/bin exists
mkdir -p ~/.local/bin

# Create symlink
ln -sf "$SCR_WRAP_PATH" ~/.local/bin/scr-wrap

echo "✅ scr-wrap installed to ~/.local/bin"
echo "Make sure ~/.local/bin is in your PATH to use 'scr-wrap' from anywhere"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo ""
    echo "⚠️  ~/.local/bin is not in your PATH"
    echo "Add this to your ~/.zshrc or ~/.bashrc:"
    echo 'export PATH="$HOME/.local/bin:$PATH"'
fi
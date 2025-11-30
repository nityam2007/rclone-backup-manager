#!/bin/bash
# Setup script for RClone Backup Manager
# This script helps you get started quickly on Linux

set -e

echo "=================================="
echo "RClone Backup Manager - Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.7 or higher."
    exit 1
fi

# Check rclone
echo "Checking rclone installation..."
if command -v rclone &> /dev/null; then
    RCLONE_VERSION=$(rclone version | head -n1 | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} rclone $RCLONE_VERSION found"
else
    echo -e "${YELLOW}!${NC} rclone not found."
    read -p "Do you want to install rclone? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing rclone..."
        curl https://rclone.org/install.sh | sudo bash
        echo -e "${GREEN}✓${NC} rclone installed"
    else
        echo -e "${RED}✗${NC} rclone is required. Please install it manually."
        exit 1
    fi
fi

# Check tkinter
echo "Checking tkinter..."
if python3 -c "import tkinter" &> /dev/null; then
    echo -e "${GREEN}✓${NC} tkinter found"
else
    echo -e "${YELLOW}!${NC} tkinter not found."
    
    # Detect package manager
    if command -v apt &> /dev/null; then
        echo "Installing python3-tk..."
        sudo apt update
        sudo apt install -y python3-tk
    elif command -v dnf &> /dev/null; then
        echo "Installing python3-tkinter..."
        sudo dnf install -y python3-tkinter
    else
        echo -e "${RED}✗${NC} Please install tkinter manually for your distribution."
        exit 1
    fi
    echo -e "${GREEN}✓${NC} tkinter installed"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt --user
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${YELLOW}!${NC} requirements.txt not found, skipping..."
fi

# Check if rclone is configured
echo ""
echo "Checking rclone configuration..."
if rclone listremotes | grep -q .; then
    echo -e "${GREEN}✓${NC} rclone remotes found:"
    rclone listremotes
else
    echo -e "${YELLOW}!${NC} No rclone remotes configured."
    read -p "Do you want to configure rclone now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rclone config
    else
        echo -e "${YELLOW}!${NC} You can configure rclone later with: rclone config"
    fi
fi

# Make script executable
chmod +x backup/backup_gui.py 2>/dev/null || true

echo ""
echo "=================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=================================="
echo ""
echo "To run the application:"
echo "  python3 backup/backup_gui.py"
echo ""
echo "To build standalone executable:"
echo "  pip3 install pyinstaller"
echo "  pyinstaller rclone_backup_gui.spec"
echo ""
echo "For more information, see:"
echo "  - README.md for full documentation"
echo "  - QUICKSTART.md for quick start guide"
echo "  - INSTALL.md for detailed installation"
echo ""
echo "Happy backing up! 🚀"

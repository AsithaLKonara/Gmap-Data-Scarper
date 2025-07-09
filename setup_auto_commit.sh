#!/bin/bash

# Setup script for automatic Git commit system
# This script installs dependencies and configures the auto-commit system

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install fswatch on macOS
install_fswatch_macos() {
    log "${YELLOW}Installing fswatch for macOS...${NC}"
    if command_exists brew; then
        brew install fswatch
        return $?
    else
        log "${RED}Homebrew not found. Please install Homebrew first:${NC}"
        log "${YELLOW}  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
        return 1
    fi
}

# Function to install inotify-tools on Linux
install_inotify_linux() {
    log "${YELLOW}Installing inotify-tools for Linux...${NC}"
    if command_exists apt-get; then
        sudo apt-get update && sudo apt-get install -y inotify-tools
        return $?
    elif command_exists yum; then
        sudo yum install -y inotify-tools
        return $?
    else
        log "${RED}Package manager not found. Please install inotify-tools manually.${NC}"
        return 1
    fi
}

# Function to make scripts executable
make_executable() {
    log "${YELLOW}Making scripts executable...${NC}"
    chmod +x auto_commit.sh
    chmod +x watch_and_commit.sh
    chmod +x commit_now.sh
    chmod +x setup_auto_commit.sh
    log "${GREEN}✓ Scripts are now executable${NC}"
}

# Function to test the system
test_system() {
    log "${YELLOW}Testing auto-commit system...${NC}"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "${RED}✗ Not in a git repository${NC}"
        return 1
    fi
    
    # Check if scripts exist
    if [[ ! -f "auto_commit.sh" ]]; then
        log "${RED}✗ auto_commit.sh not found${NC}"
        return 1
    fi
    
    log "${GREEN}✓ Auto-commit system is ready!${NC}"
    return 0
}

# Function to show usage instructions
show_instructions() {
    log "${GREEN}🎉 Auto-commit system setup complete!${NC}"
    log ""
    log "${YELLOW}Usage Instructions:${NC}"
    log ""
    log "${BLUE}1. Start automatic file watching:${NC}"
    log "   ./watch_and_commit.sh"
    log ""
    log "${BLUE}2. Manual commit:${NC}"
    log "   ./commit_now.sh"
    log ""
    log "${BLUE}3. One-time auto-commit:${NC}"
    log "   ./auto_commit.sh"
    log ""
    log "${YELLOW}The system will automatically:${NC}"
    log "  ✓ Watch for file changes"
    log "  ✓ Generate descriptive commit messages"
    log "  ✓ Commit and push to Git"
    log "  ✓ Show colored progress output"
    log ""
    log "${GREEN}Start coding and your changes will be automatically saved! 🚀${NC}"
}

# Main setup function
main() {
    log "${BLUE}🔧 Setting up automatic Git commit system...${NC}"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "${RED}✗ Not in a git repository${NC}"
        log "${YELLOW}Please run this script from your project directory${NC}"
        exit 1
    fi
    
    # Make scripts executable
    make_executable
    
    # Detect OS and install dependencies
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        log "${YELLOW}Detected macOS${NC}"
        if ! command_exists fswatch; then
            if install_fswatch_macos; then
                log "${GREEN}✓ fswatch installed successfully${NC}"
            else
                log "${RED}✗ Failed to install fswatch${NC}"
                exit 1
            fi
        else
            log "${GREEN}✓ fswatch already installed${NC}"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        log "${YELLOW}Detected Linux${NC}"
        if ! command_exists inotifywait; then
            if install_inotify_linux; then
                log "${GREEN}✓ inotify-tools installed successfully${NC}"
            else
                log "${RED}✗ Failed to install inotify-tools${NC}"
                exit 1
            fi
        else
            log "${GREEN}✓ inotify-tools already installed${NC}"
        fi
    else
        log "${RED}✗ Unsupported OS: $OSTYPE${NC}"
        log "${YELLOW}Please install file watching tools manually:${NC}"
        log "  - macOS: brew install fswatch"
        log "  - Linux: sudo apt-get install inotify-tools"
        exit 1
    fi
    
    # Test the system
    if test_system; then
        show_instructions
    else
        log "${RED}✗ Setup failed${NC}"
        exit 1
    fi
}

# Run the main function
main "$@" 
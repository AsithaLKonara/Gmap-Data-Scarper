#!/bin/bash

# File watcher script for automatic Git commits
# This script watches for file changes and automatically commits them

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

# Function to check if fswatch is available
check_fswatch() {
    if command -v fswatch >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to install fswatch (macOS)
install_fswatch() {
    log "${YELLOW}fswatch not found. Installing...${NC}"
    if command -v brew >/dev/null 2>&1; then
        brew install fswatch
        return $?
    else
        log "${RED}Homebrew not found. Please install fswatch manually:${NC}"
        log "${YELLOW}  brew install fswatch${NC}"
        return 1
    fi
}

# Function to watch files and auto-commit
watch_and_commit() {
    log "${GREEN}🚀 Starting file watcher...${NC}"
    log "${YELLOW}Watching for changes in:${NC}"
    log "  - backend/"
    log "  - frontend/"
    log "  - *.py"
    log "  - *.tsx"
    log "  - *.ts"
    log "  - *.js"
    log "  - *.json"
    log "  - *.md"
    log "  - *.yml"
    log "  - *.yaml"
    log ""
    log "${GREEN}Press Ctrl+C to stop watching${NC}"
    log ""

    # Watch for changes and run auto-commit
    fswatch -o \
        backend/ \
        frontend/ \
        *.py \
        *.tsx \
        *.ts \
        *.js \
        *.json \
        *.md \
        *.yml \
        *.yaml \
        docker-compose.yml \
        Dockerfile* \
        .env* \
        README.md \
        package.json \
        requirements.txt | while read f; do
        log "${YELLOW}📁 File change detected! Running auto-commit...${NC}"
        ./auto_commit.sh
        log "${GREEN}✅ Auto-commit completed${NC}"
        log ""
    done
}

# Function to watch files using inotifywait (Linux alternative)
watch_and_commit_linux() {
    log "${GREEN}🚀 Starting file watcher (Linux)...${NC}"
    log "${YELLOW}Watching for changes...${NC}"
    log "${GREEN}Press Ctrl+C to stop watching${NC}"
    log ""

    # Watch for changes and run auto-commit
    inotifywait -m -r -e modify,create,delete \
        backend/ \
        frontend/ \
        . \
        --exclude node_modules \
        --exclude .git \
        --exclude __pycache__ \
        --exclude *.pyc | while read path action file; do
        log "${YELLOW}📁 File change detected: $file${NC}"
        ./auto_commit.sh
        log "${GREEN}✅ Auto-commit completed${NC}"
        log ""
    done
}

# Function to watch files using fswatch (macOS)
watch_and_commit_macos() {
    log "${GREEN}🚀 Starting file watcher (macOS)...${NC}"
    log "${YELLOW}Watching for changes...${NC}"
    log "${GREEN}Press Ctrl+C to stop watching${NC}"
    log ""

    # Watch for changes and run auto-commit
    fswatch -o \
        backend/ \
        frontend/ \
        *.py \
        *.tsx \
        *.ts \
        *.js \
        *.json \
        *.md \
        *.yml \
        *.yaml \
        docker-compose.yml \
        Dockerfile* \
        .env* \
        README.md \
        package.json \
        requirements.txt | while read f; do
        log "${YELLOW}📁 File change detected! Running auto-commit...${NC}"
        ./auto_commit.sh
        log "${GREEN}✅ Auto-commit completed${NC}"
        log ""
    done
}

# Main execution
main() {
    log "${BLUE}🔍 Setting up automatic Git commits...${NC}"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "${RED}✗ Not in a git repository${NC}"
        exit 1
    fi
    
    # Check if auto_commit.sh exists
    if [[ ! -f "auto_commit.sh" ]]; then
        log "${RED}✗ auto_commit.sh not found${NC}"
        exit 1
    fi
    
    # Make sure auto_commit.sh is executable
    chmod +x auto_commit.sh
    
    # Detect OS and use appropriate file watcher
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if check_fswatch; then
            watch_and_commit_macos
        else
            if install_fswatch; then
                watch_and_commit_macos
            else
                log "${RED}✗ Failed to install fswatch${NC}"
                exit 1
            fi
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v inotifywait >/dev/null 2>&1; then
            watch_and_commit_linux
        else
            log "${RED}✗ inotifywait not found. Please install it:${NC}"
            log "${YELLOW}  sudo apt-get install inotify-tools${NC}"
            exit 1
        fi
    else
        log "${RED}✗ Unsupported OS: $OSTYPE${NC}"
        log "${YELLOW}Please install fswatch (macOS) or inotify-tools (Linux)${NC}"
        exit 1
    fi
}

# Run the main function
main "$@" 
#!/bin/bash

# Manual commit script for immediate commits
# Usage: ./commit_now.sh [optional commit message]

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

# Function to get commit message
get_commit_message() {
    if [[ -n "$1" ]]; then
        echo "$1"
    else
        local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
        local changed_files=$(git status --porcelain | wc -l)
        echo "🔄 Manual commit: Updated $changed_files files - $timestamp"
    fi
}

# Function to commit and push
commit_and_push() {
    local commit_msg="$1"
    
    log "${YELLOW}Committing and pushing changes...${NC}"
    
    # Check if there are changes
    if [[ -z $(git status --porcelain) ]]; then
        log "${YELLOW}No changes to commit${NC}"
        return 0
    fi
    
    # Add all changes
    git add .
    
    # Commit
    if git commit -m "$commit_msg"; then
        log "${GREEN}✓ Successfully committed changes${NC}"
        
        # Push to remote
        if git push origin main; then
            log "${GREEN}✓ Successfully pushed to remote${NC}"
            log "${GREEN}✓ Manual commit completed successfully!${NC}"
        else
            log "${RED}✗ Failed to push to remote${NC}"
            return 1
        fi
    else
        log "${RED}✗ Failed to commit changes${NC}"
        return 1
    fi
}

# Main execution
main() {
    log "${BLUE}🚀 Manual commit script started${NC}"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "${RED}✗ Not in a git repository${NC}"
        exit 1
    fi
    
    # Get commit message
    local commit_message=$(get_commit_message "$1")
    
    # Commit and push
    commit_and_push "$commit_message"
}

# Run the main function
main "$@" 
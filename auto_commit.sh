#!/bin/bash

# Auto-commit script for LeadTap SaaS Platform
# This script automatically commits and pushes changes

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

# Function to check if there are changes to commit
check_changes() {
    if [[ -n $(git status --porcelain) ]]; then
        return 0  # Changes exist
    else
        return 1  # No changes
    fi
}

# Function to get a descriptive commit message
get_commit_message() {
    local changed_files=$(git status --porcelain | wc -l)
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    # Get list of changed file types
    local file_types=$(git status --porcelain | grep -E '\.(py|tsx|ts|js|css|json|md|yml|yaml)$' | sed 's/.*\.//' | sort | uniq | tr '\n' ',' | sed 's/,$//')
    
    if [[ -n "$file_types" ]]; then
        echo "🔄 Auto-commit: Updated $changed_files files ($file_types) - $timestamp"
    else
        echo "🔄 Auto-commit: Updated $changed_files files - $timestamp"
    fi
}

# Function to commit and push changes
commit_and_push() {
    local commit_msg="$1"
    
    log "${YELLOW}Changes detected! Committing and pushing...${NC}"
    
    # Add all changes
    git add .
    
    # Commit with the provided message
    if git commit -m "$commit_msg"; then
        log "${GREEN}✓ Successfully committed changes${NC}"
        
        # Push to remote
        if git push origin main; then
            log "${GREEN}✓ Successfully pushed to remote${NC}"
            log "${GREEN}✓ Auto-commit completed successfully!${NC}"
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
    log "${BLUE}🚀 Auto-commit script started${NC}"
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log "${RED}✗ Not in a git repository${NC}"
        exit 1
    fi
    
    # Check if there are changes to commit
    if check_changes; then
        local commit_message=$(get_commit_message)
        commit_and_push "$commit_message"
    else
        log "${YELLOW}No changes to commit${NC}"
    fi
}

# Run the main function
main "$@" 
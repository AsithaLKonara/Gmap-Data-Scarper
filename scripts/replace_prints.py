"""Script to replace print() statements with logging."""
import re
import os
from pathlib import Path

# Files to process
FILES_TO_PROCESS = [
    "backend/services/retention_service.py",
    "backend/services/postgresql_cache.py",
    "backend/services/stream_service.py",
    "backend/services/chrome_pool.py",
    "backend/services/ai_enrichment.py",
    "backend/services/company_intelligence.py",
    "backend/services/push_service.py",
    "backend/services/stripe_service.py",
    "backend/services/email_extractor.py",
    "backend/services/zoho_crm.py",
    "backend/services/template_service.py",
    "backend/services/ai_query_generator.py",
    "backend/services/anti_detection.py",
    "backend/routes/legal.py",
]

def replace_prints_in_file(filepath: str):
    """Replace print() statements with logging in a file."""
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Check if logging is imported
    has_logging_import = 'import logging' in content or 'from logging import' in content
    
    # Replace print() patterns
    # Pattern 1: print(f"...") -> logging.info(f"...")
    content = re.sub(
        r'print\(f"([^"]+)"\)',
        r'logging.info(f"\1")',
        content
    )
    
    # Pattern 2: print("...") -> logging.info("...")
    content = re.sub(
        r'print\("([^"]+)"\)',
        r'logging.info("\1")',
        content
    )
    
    # Pattern 3: print(f'...') -> logging.info(f'...')
    content = re.sub(
        r"print\(f'([^']+)'\)",
        r"logging.info(f'\1')",
        content
    )
    
    # Pattern 4: print('...') -> logging.info('...')
    content = re.sub(
        r"print\('([^']+)'\)",
        r"logging.info('\1')",
        content
    )
    
    # Add logging import if needed and content changed
    if content != original_content and not has_logging_import:
        # Find the last import statement
        import_pattern = r'(^import |^from .* import)'
        lines = content.split('\n')
        last_import_idx = -1
        for i, line in enumerate(lines):
            if re.match(import_pattern, line.strip()):
                last_import_idx = i
        
        if last_import_idx >= 0:
            lines.insert(last_import_idx + 1, 'import logging')
            content = '\n'.join(lines)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated: {filepath}")
        return True
    else:
        print(f"⏭️  No changes: {filepath}")
        return False

if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    updated_count = 0
    
    for filepath in FILES_TO_PROCESS:
        full_path = base_dir / filepath
        if replace_prints_in_file(str(full_path)):
            updated_count += 1
    
    print(f"\n✅ Updated {updated_count} files")


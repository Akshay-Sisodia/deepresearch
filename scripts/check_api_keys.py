#!/usr/bin/env python3
"""
Script to check for potential API keys in the codebase.
This helps ensure no API keys are accidentally committed to the repository.
"""

import os
import re
import sys
import argparse
from typing import List, Tuple, Set

# Patterns that might indicate API keys
API_KEY_PATTERNS = [
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI/OpenRouter style keys
    r'sk-or-[a-zA-Z0-9\-]{50,}',  # OpenRouter style keys
    r'[a-f0-9]{32,}',  # Generic hex strings (potential API keys)
    r'[A-Za-z0-9_\-]{32,}',  # Generic alphanumeric strings (potential API keys)
    r'api[_\-]?key["\']?\s*[=:]\s*["\']([^"\']+)["\']',  # api_key = "value"
    r'token["\']?\s*[=:]\s*["\']([^"\']+)["\']',  # token = "value"
    r'secret["\']?\s*[=:]\s*["\']([^"\']+)["\']',  # secret = "value"
    r'password["\']?\s*[=:]\s*["\']([^"\']+)["\']',  # password = "value"
]

# Files and directories to ignore
IGNORE_DIRS = [
    '.git',
    'venv',
    'env',
    '__pycache__',
    'node_modules',
    'dist',
    'build',
]

IGNORE_FILES = [
    '.env.example',
    'check_api_keys.py',  # Ignore this script itself
]

# File extensions to check
CHECK_EXTENSIONS = [
    '.py',
    '.js',
    '.ts',
    '.json',
    '.yaml',
    '.yml',
    '.toml',
    '.md',
    '.txt',
    '.html',
    '.css',
    '.sh',
    '.bat',
    '.ps1',
    '.env',
]

def is_ignored(path: str) -> bool:
    """Check if a path should be ignored."""
    # Check if any part of the path is in IGNORE_DIRS
    parts = path.split(os.sep)
    for part in parts:
        if part in IGNORE_DIRS:
            return True
            
    # Check if the file is in IGNORE_FILES
    filename = os.path.basename(path)
    if filename in IGNORE_FILES:
        return True
        
    # Check if the file has an extension we care about
    _, ext = os.path.splitext(filename)
    if ext and ext not in CHECK_EXTENSIONS:
        return True
        
    return False

def find_api_keys(content: str, filename: str) -> List[Tuple[str, int, str]]:
    """Find potential API keys in content."""
    results = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        for pattern in API_KEY_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Skip if this is just a variable name or placeholder
                matched_text = match.group(0)
                if any(placeholder in matched_text.lower() for placeholder in 
                      ['your_', 'your-', 'placeholder', 'example', '<', '>']):
                    continue
                    
                # Skip if this is in a comment
                if line.strip().startswith('#') or line.strip().startswith('//'):
                    continue
                    
                results.append((filename, i + 1, line.strip()))
                break  # Only report each line once
    
    return results

def scan_directory(directory: str) -> List[Tuple[str, int, str]]:
    """Scan a directory for files with potential API keys."""
    results = []
    
    for root, dirs, files in os.walk(directory):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            if is_ignored(filepath):
                continue
                
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                file_results = find_api_keys(content, filepath)
                results.extend(file_results)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Check for potential API keys in codebase')
    parser.add_argument('--directory', '-d', default='.', help='Directory to scan')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show verbose output')
    
    args = parser.parse_args()
    
    print(f"Scanning {args.directory} for potential API keys...")
    results = scan_directory(args.directory)
    
    if results:
        print(f"\n⚠️  Found {len(results)} potential API keys:")
        for filename, line_num, line in results:
            print(f"\n{filename}:{line_num}")
            print(f"  {line}")
        
        print("\n⚠️  Please remove these API keys and use environment variables instead.")
        print("   Add sensitive files to .gitignore to prevent accidental commits.")
        return 1
    else:
        print("\n✅ No potential API keys found!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 
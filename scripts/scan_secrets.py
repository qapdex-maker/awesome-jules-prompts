#!/usr/bin/env python3
import os
import re
import sys

PATTERNS = {
    "Generic Token": r"(?i)(api_key|secret|token|passwd|private_key)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{16,}['\"]",
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{32,}",
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "Google API Key": r"AIzaSy[A-Za-z0-9_-]{33}",
}

def scan_file(filepath):
    found_issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_no, line in enumerate(f, 1):
                for label, pattern in PATTERNS.items():
                    if re.search(pattern, line):
                        if "{" in line and "}" in line:
                            continue
                        found_issues.append((line_no, label, line.strip()))
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return found_issues

def main():
    failed = False
    for root, _, files in os.walk('.'):
        if any(ignored in root for ignored in ['.git', 'node_modules', 'assets']):
            continue
        for file in files:
            filepath = os.path.join(root, file)
            issues = scan_file(filepath)
            if issues:
                failed = True
                print(f"⚠️ Potential Secret Leak in {filepath}:")
                for line_no, label, line in issues:
                    print(f"  Line {line_no}: {label} - {line[:60]}...")
    if failed:
        sys.exit(1)
    print("✅ No potential secrets detected.")

if __name__ == "__main__":
    main()

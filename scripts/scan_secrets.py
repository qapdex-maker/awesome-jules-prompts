#!/usr/bin/env python3
import os
import re
import sys

# ⚡ Bolt: Pre-compile regex patterns for better performance
PATTERNS = {
    "Generic Token": re.compile(r"(?i)(api_key|secret|token|passwd|private_key)\s*[:=]\s*['\"](?:\{[a-zA-Z0-9_\-]+\}|[a-zA-Z0-9_\-]{16,})['\"]"),
    "OpenAI API Key": re.compile(r"sk-(?:[a-zA-Z0-9_\-]{32,}|\{[a-zA-Z0-9_\-]+\})"),
    "AWS Access Key": re.compile(r"(?:AKIA|ASIA)(?:[0-9A-Z]{16}|\{[a-zA-Z0-9_\-]+\})"),
    "Google API Key": re.compile(r"AIzaSy(?:[A-Za-z0-9_-]{33}|\{[a-zA-Z0-9_\-]+\})"),
}

def scan_file(filepath):
    found_issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # ⚡ Bolt & Sentinel: Perform a fast whole-file pre-filter check
        if not any(cp.search(content) for cp in PATTERNS.values()):
            return found_issues

        # Detailed line-by-line scanning only if a potential match exists
        lines = content.splitlines()
        for line_no, line in enumerate(lines, 1):
            for label, cp in PATTERNS.items():
                for match in cp.finditer(line):
                    matched_str = match.group(0)
                    if "{" in matched_str and "}" in matched_str:
                        continue
                    found_issues.append((line_no, label, line.strip()))
                    break
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return found_issues

def main():
    failed = False
    # ⚡ Bolt: Use directory pruning to skip ignored folders efficiently
    ignored_dirs = {'.git', 'node_modules', 'assets', '__pycache__', '.pytest_cache'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
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

#!/usr/bin/env python3
import os
import re
import sys

# ⚡ Bolt: Pre-compile regex patterns for better performance
PATTERNS = {
    "Generic Token": re.compile(r"(?i)(api_key|secret|token|passwd|private_key)\s*[:=]\s*['\"](?:\{[a-zA-Z0-9_\-]+\}|[a-zA-Z0-9_\-]{16,})['\"]"),
    "OpenAI API Key": re.compile(r"sk-(?!ant-)(?:[a-zA-Z0-9_\-]{32,}|\{[a-zA-Z0-9_\-]+\})"),
    "AWS Access Key": re.compile(r"(?:AKIA|ASIA)(?:[0-9A-Z]{16}|\{[a-zA-Z0-9_\-]+\})"),
    "Google API Key": re.compile(r"AIzaSy(?:[A-Za-z0-9_-]{33}|\{[a-zA-Z0-9_\-]+\})"),
    "GitHub Token": re.compile(r"(?:gh[pousr]_|github_pat_)(?:[a-zA-Z0-9_]{36,}|\{[a-zA-Z0-9_\-]+\})"),
    "Anthropic API Key": re.compile(r"sk-ant-(?:[a-zA-Z0-9_\-]{40,}|\{[a-zA-Z0-9_\-]+\})"),
}

def scan_file(filepath):
    found_issues = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # ⚡ Bolt & Sentinel: Perform a fast whole-file pre-filter check
        if not any(cp.search(content) for cp in PATTERNS.values()):
            return found_issues

        # ⚡ Bolt: Detailed whole-file scanning only if a potential match exists.
        # Scanning the whole content in one pass via regex is significantly faster
        # than splitting the file into thousands of lines and scanning each line.
        reported_issues = set()
        for label, cp in PATTERNS.items():
            for match in cp.finditer(content):
                matched_str = match.group(0)
                if "{" in matched_str and "}" in matched_str:
                    continue
                start_pos = match.start()
                # Dynamically calculate the line number (count of preceding newlines)
                line_no = content.count('\n', 0, start_pos) + 1

                # Maintain original behavior: report at most one secret of each label per line
                if (line_no, label) in reported_issues:
                    continue
                reported_issues.add((line_no, label))

                # Dynamically extract only the matching line content
                line_start = content.rfind('\n', 0, start_pos) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end]
                found_issues.append((line_no, label, line.strip()))

        # Maintain consistent sorted output by line number
        found_issues.sort(key=lambda x: x[0])
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

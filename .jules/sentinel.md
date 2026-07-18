<!-- markdownlint-disable MD041 -->
[← Back to Main README](../README.md)

---

## 2026-07-14 - [Automated Pre-Commit Secret Scanning]

**Vulnerability:** Accidental exposure of API keys, OpenAI tokens, AWS
credentials, or other secrets in prompt examples or documentation
contributions.

**Learning:** Even in documentation-only repositories (e.g., awesome prompt
lists), there is a significant risk of contributors inadvertently committing
real credentials when sharing their prompts or example configurations. Since
standard code-centric tools might not be configured for pure Markdown repos, a
lightweight and localized script is needed to prevent credential leakage.

**Prevention:** Implement a clean, dependency-free Python pre-commit/CI script
(`scripts/scan_secrets.py`) utilizing regex patterns to validate file contents
before changes are committed, raising failures on potential high-entropy
credentials.

## 2026-07-16 - [Secret Scan Bypass via Template Comments]

**Vulnerability:** A naive line-level check for curly braces (`"{" in line and
"}" in line`) in `scan_secrets.py` allowed real secrets to bypass scanning
completely if a prompt placeholder or curly brace comment existed anywhere on
the same line.

**Learning:** Line-level heuristic bypasses can easily create security gaps when
multiple patterns coexist (e.g., a real API key and an unrelated
placeholder/comment on the same line). Filtering must be precisely targeted at
the matched secret string rather than broad line-level heuristics.

**Prevention:** Refine secret scanning regex patterns to explicitly match both
normal secrets and placeholder formats, then check if curly braces are present
within the matched substring (`match.group(0)`) rather than the entire line
before skipping.

## 2026-07-17 - [Secret Scan Bypass via Single-Line Multiple Matches]

**Vulnerability:** The secret scanning script `scan_secrets.py` utilized
`re.search()` to evaluate matches. This returned only the first match on any
given line. If a line contained a placeholder (e.g., `sk-{API_KEY}`) followed
by a real secret (e.g., a real API key) on the same line, the script matched
the placeholder first, saw it had curly braces, and skipped scanning the line
entirely, bypassing security checks and leaking the real secret.

**Learning:** When using regular expressions to scan files line-by-line, relying
on single-match search functions can lead to blind spots if multiple matched
structures (e.g., dummy template placeholders and actual secrets) coexist on
the same line.

**Prevention:** Always iterate through all matches on a line using `finditer()`
(or global/multiline flags) and only skip the line if *all* matched occurrences
are valid, non-leaking patterns or placeholders.

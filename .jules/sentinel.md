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

## 2026-07-18 - [Modern OpenAI Key Bypass in Secret Scanner]

**Vulnerability:** Modern OpenAI API key formats containing hyphens and
underscores (e.g., `sk-proj-`) bypassed the secret scanner entirely because
the regex pattern restrictively matched only alphanumeric characters
`[a-zA-Z0-9]{32,}`.

**Learning:** Regex definitions must be periodically updated to match the
evolving formats of modern keys and credentials. Without proper coverage
for special characters like hyphens or underscores in key prefixes, scanning
tools suffer from false negatives and allow credentials to be leaked silently.

**Prevention:** Broaden pattern matching characters to allow `[a-zA-Z0-9_\-]`
in credential payloads, and verify regex coverage through dedicated unit tests
(`test_scan_secrets.py`) that simulate modern key formats using dynamic
concatenation.

## 2026-07-21 - [GitHub Token Bypass in Secret Scanner]

**Vulnerability:** The repository's secret scanner lacked pattern definitions
to detect leaked classic or fine-grained GitHub Personal Access Tokens (PATs)
and other GitHub credentials.

**Learning:** When scanning for developer-centric credentials in repositories
with high contributor volume (even doc-only), ignoring common platform-specific
credential formats like `ghp_` or `github_pat_` creates a blind spot.
Furthermore, overlapping rules (e.g., a "Generic Token" keyword rule and a specific
"GitHub Token" rule) can trigger dual/overlapping matches if variables or test cases
unintentionally share keywords like `github_token`.

**Prevention:** Add explicit pattern definitions covering all classic, fine-grained,
and temp/installation GitHub token formats to `scan_secrets.py`. When writing tests
for specific patterns, avoid using generic keywords in assignment statements
to prevent rule collisions.

## 2026-07-23 - [Leaked Groq and Replicate AI Credentials]

**Vulnerability:** Lack of dedicated secret scanner patterns for popular AI
developer services like Groq and Replicate. This created a potential blind
spot where developers contributing prompt configurations or example integrations
could accidentally leak live `gsk_` Groq keys or `r8_` Replicate API tokens.

**Learning:** In AI-centric and prompt-curation repositories, the threat model
extends beyond generic or classic cloud credentials to modern AI-native service
API keys. Coverage must be kept complete by adding specific rules for rising
and widely adopted AI platforms.

**Prevention:** Regularly audit active prompt examples and expand the pre-commit
scanner (`scan_secrets.py`) patterns to cover specialized AI API credential
formats as they emerge, verifying each with dedicated unit tests.

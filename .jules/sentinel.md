<!-- markdownlint-disable MD041 -->

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

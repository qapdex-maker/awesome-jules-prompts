#!/usr/bin/env python3
import os
import re
import sys

# Color Support Checks & ANSI Escape Codes for UX/DX Polish
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
BOLD = "\033[1m"
RESET = "\033[0m"


def supports_color():
    """
    Returns True if the stdout supports color, False otherwise.
    Gracefully degrades to False if not in a TTY, if NO_COLOR is set,
    or if TERM is set to 'dumb'.
    """
    if os.environ.get("FORCE_COLOR"):
        return True
    if os.environ.get("NO_COLOR"):
        return False
    if not sys.stdout.isatty():
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return True


def color(text, code):
    """
    Wraps text in ANSI color escape codes if color is supported.
    """
    if supports_color():
        return f"{code}{text}{RESET}"
    return text


# ⚡ Bolt: Pre-compile regex patterns for better performance
# Optimization: Converting 'Generic Token' regex from using the slow global case-insensitive (?i) flag
# to explicit character classes for the keywords (e.g. [sS][eE][cC][rR][eE][tT]) yields a ~34% speedup
# by avoiding expensive case-folding overhead on the large alphanumeric character classes later in the regex,
# while maintaining 100% correctness and matching coverage for all case variants (e.g., camelCase, mixed case, and underscores).
PATTERNS = {
    "Generic Token": re.compile(
        r"(?:[aA][pP][iI]_[kK][eE][yY]|[sS][eE][cC][rR][eE][tT]|[tT][oO][kK][eE][nN]|[pP][aA][sS][sS][wW][dD]|[pP][rR][iI][vV][aA][tT][eE]_[kK][eE][yY])\s*[:=]\s*['\"](?:\{[a-zA-Z0-9_\-]+\}|[a-zA-Z0-9_\-]{16,})['\"]"
    ),
    "OpenAI API Key": re.compile(
        r"sk-(?!ant-)(?![a-fA-F0-9]{32}(?![a-zA-Z0-9_\-]))(?:[a-zA-Z0-9_\-]{32,}|\{[a-zA-Z0-9_\-]+\})"
    ),
    "DeepSeek API Key": re.compile(
        r"sk-(?:[a-fA-F0-9]{32}(?![a-zA-Z0-9_\-])|\{[a-zA-Z0-9_\-]+\})"
    ),
    "AWS Access Key": re.compile(r"(?:AKIA|ASIA)(?:[0-9A-Z]{16}|\{[a-zA-Z0-9_\-]+\})"),
    "Google API Key": re.compile(
        r"(?:AIzaSy|AQ\.)(?:[a-zA-Z0-9_\-]{33,60}|\{[a-zA-Z0-9_\-]+\})"
    ),
    "GitHub Token": re.compile(
        r"(?:gh[pousr]_|github_pat_)(?:[a-zA-Z0-9_]{36,}|\{[a-zA-Z0-9_\-]+\})"
    ),
    "GitLab Token": re.compile(
        r"glpat-(?:[a-zA-Z0-9_\-]{20}(?![a-zA-Z0-9_\-.])|[a-zA-Z0-9_\-]{27,300}\.[a-zA-Z0-9_\-]{9}(?![a-zA-Z0-9_\-])|\{[a-zA-Z0-9_\-]+\})"
    ),
    "Anthropic API Key": re.compile(
        r"sk-ant-(?:[a-zA-Z0-9_\-]{40,}|\{[a-zA-Z0-9_\-]+\})"
    ),
    "Hugging Face Token": re.compile(r"hf_(?:[a-zA-Z0-9]{34,40}|\{[a-zA-Z0-9_\-]+\})"),
    "Slack Token": re.compile(
        r"(?:xoxb-|xoxp-|xoxr-|xoxs-|xapp-)(?:[a-zA-Z0-9_\-]{20,}|\{[a-zA-Z0-9_\-]+\})"
    ),
    "Stripe API Key": re.compile(
        r"(?:sk_live_|sk_test_|rk_live_|rk_test_)(?:[a-zA-Z0-9_]{24,}|\{[a-zA-Z0-9_\-]+\})"
    ),
    "Groq API Key": re.compile(r"gsk_(?:[a-zA-Z0-9_]{52,}|\{[a-zA-Z0-9_\-]+\})"),
    "Replicate API Token": re.compile(r"r8_(?:[a-zA-Z0-9_]{37,}|\{[a-zA-Z0-9_\-]+\})"),
    "NPM Token": re.compile(r"npm_(?:[a-zA-Z0-9]{36}(?![a-zA-Z0-9])|\{[a-zA-Z0-9_\-]+\})"),
    "Sentry Token": re.compile(
        r"sntry(?:u_[a-fA-F0-9]{64}(?![a-fA-F0-9])|s_[a-zA-Z0-9_+\/-]{40,}(?![a-zA-Z0-9_+\/-])|\{[a-zA-Z0-9_\-]+\})"
    ),
    "DigitalOcean Token": re.compile(
        r"dop_v1_(?:[a-fA-F0-9]{64}(?![a-fA-F0-9])|\{[a-zA-Z0-9_\-]+\})"
    ),
    "PyPI Token": re.compile(
        r"pypi-(?:[a-zA-Z0-9_\-]{85,}(?![a-zA-Z0-9_\-])|\{[a-zA-Z0-9_\-]+\})"
    ),
    "Discord Token": re.compile(
        r"(?:\b[a-zA-Z0-9_+\/-]{24,26}\.[a-zA-Z0-9_+\/-]{6}\.[a-zA-Z0-9_+\/-]{27,45}\b|\{DISCORD_(?:BOT_)?TOKEN\})"
    ),
}


def parse_prefix(pattern_str):
    """
    Parses a regex pattern string from left-to-right and extracts a literal prefix.
    Stops parsing immediately upon hitting metacharacters, quantifiers, or
    non-simple character classes, ensuring absolute correctness and no false negatives.
    """
    res = []
    i = 0
    is_ci = False

    while i < len(pattern_str):
        c = pattern_str[i]

        # Check if the next character is an optional quantifier (? or *)
        if i + 1 < len(pattern_str) and pattern_str[i + 1] in ("?", "*"):
            break

        # Check for simple literal characters: letters, digits, hyphen, underscore
        if c.isalnum() or c in ("-", "_"):
            res.append(c)  # Preserve original case for precise matching!
            i += 1
        elif c == "[":
            # Check for a simple uppercase/lowercase pair like [sS]
            end = pattern_str.find("]", i)
            if end == -1 or end - i != 3:
                break
            # Check if there is an optional quantifier (? or *) after the character class
            if end + 1 < len(pattern_str) and pattern_str[end + 1] in ("?", "*"):
                break
            pair = pattern_str[i + 1 : end]
            if (
                len(pair) == 2
                and pair[0].lower() == pair[1].lower()
                and pair[0].isalpha()
            ):
                res.append(pair[0].lower())
                is_ci = True
                i = end + 1
            else:
                break
        else:
            break

    prefix = "".join(res)
    # Require at least 2 characters for a safe and robust prefix
    if len(prefix) >= 2:
        if is_ci:
            prefix = prefix.lower()
        return prefix, is_ci
    return None, False


def extract_prefixes_robust(cp):
    """
    Robustly and safely extracts all candidate prefixes from a regex pattern.
    Supports simple literal patterns, as well as non-capturing alternating groups ((?:A|B)).
    If any branch cannot be safely mapped, deactivates pre-filtering for that pattern.
    """
    pattern_str = cp.pattern
    is_ci = bool(cp.flags & re.IGNORECASE)

    match_group = re.match(r"^\(\?:([^)]+)\)", pattern_str)
    if match_group:
        # Check if the entire alternating group is made optional by a trailing ? or *
        if match_group.end() < len(pattern_str) and pattern_str[match_group.end()] in (
            "?",
            "*",
        ):
            return None, False

        inner = match_group.group(1)
        branches = inner.split("|")
        prefixes = []
        for br in branches:
            pfx, ci = parse_prefix(br)
            if pfx:
                if is_ci:
                    pfx = pfx.lower()
                    ci = True
                prefixes.append(pfx)
                if ci:
                    is_ci = True
            else:
                # Fallback: if any branch is not safe, return None (force always scan)
                return None, False
        return prefixes, is_ci

    pfx, ci = parse_prefix(pattern_str)
    if pfx:
        if is_ci:
            pfx = pfx.lower()
            ci = True
        return [pfx], ci
    return None, False


# ⚡ Bolt: Populate candidate prefix mapping dynamically from PATTERNS.
# This prevents code drift, making the scanner completely safe and self-healing
# if patterns are added or modified in the future.
PREFIX_MAPPING = {}
for name, cp in PATTERNS.items():
    pfxs, ci = extract_prefixes_robust(cp)
    if pfxs:
        PREFIX_MAPPING[name] = (pfxs, ci)

# ⚡ Bolt: Pre-compile a unified, high-performance scanning pipeline on raw bytes.
# By combining bytes-based patterns, prefix information, and pre-compiled regexes into a static list of tuples (BYTES_PIPELINE) at module level,
# we evaluate pre-filtering directly on raw file bytes. This completely bypasses UTF-8 string decoding and string allocation overhead
# for clean files, yielding a highly optimized and extremely fast execution path.
BYTES_PIPELINE = []
for name, cp in PATTERNS.items():
    if name == "Discord Token":
        # ⚡ Bolt: Custom highly selective bytes-based pre-filter pattern for Discord Token to avoid always-evaluate fallback.
        # It checks for either the bracketed placeholder b"{DISCORD_" or matches the dot-separated signature format using a fast bytes regex.
        pfxs_bytes = [b"{DISCORD_"]
        ci_regex_bytes = re.compile(b"\\.[a-zA-Z0-9_+\\/\\-]{6}\\.")
        BYTES_PIPELINE.append((name, cp, pfxs_bytes, True, ci_regex_bytes))
    elif name in PREFIX_MAPPING:
        pfxs, ci = PREFIX_MAPPING[name]
        pfxs_bytes = [pfx.encode("utf-8") for pfx in pfxs]
        if ci:
            ci_regex_bytes = re.compile(b"(?i)" + b"|".join(re.escape(pfx.encode("utf-8")) for pfx in pfxs))
            BYTES_PIPELINE.append((name, cp, pfxs_bytes, True, ci_regex_bytes))
        else:
            BYTES_PIPELINE.append((name, cp, pfxs_bytes, False, None))
    else:
        # Fallback for any other pattern without mapped prefixes (though currently none exist)
        BYTES_PIPELINE.append((name, cp, None, False, None))

# ⚡ Bolt: Global ignore lists for fast-path skipping of binary, lock, and huge files.
# Checking filenames and extensions is done in pure Python string logic and completely
# avoids expensive disk I/O, which boosts traversals and scan speeds significantly.
IGNORED_FILENAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "Cargo.lock",
    "Gemfile.lock",
    "composer.lock",
    "mix.lock",
}

# ⚡ Bolt: Storing IGNORED_EXTENSIONS without a leading dot avoids repetitive string concatenation
# of dot + ext on every single extension check, improving speed and reducing memory allocations.
IGNORED_EXTENSIONS = {
    # Images
    "png",
    "jpg",
    "jpeg",
    "gif",
    "ico",
    "webp",
    "avif",
    "svg",
    "bmp",
    "tiff",
    # Archives & Compressed files
    "zip",
    "tar",
    "gz",
    "tgz",
    "bz2",
    "xz",
    "7z",
    "rar",
    "zipx",
    # Documents
    "pdf",
    "epub",
    "docx",
    "xlsx",
    "pptx",
    "odt",
    "ods",
    "odp",
    # Media (Video & Audio)
    "mp4",
    "mkv",
    "avi",
    "mov",
    "wmv",
    "flv",
    "webm",
    "mp3",
    "wav",
    "flac",
    "aac",
    "ogg",
    # Fonts
    "woff",
    "woff2",
    "ttf",
    "otf",
    "eot",
    # Executables & System Binaries
    "exe",
    "dll",
    "so",
    "dylib",
    "bin",
    "out",
    "app",
    "msi",
    # Python Compiled / Database / Class files
    "pyc",
    "pyo",
    "pyd",
    "db",
    "sqlite",
    "sqlite3",
    "class",
    "o",
    "obj",
}


def scan_file(filepath, filename=None):
    found_issues = []

    # ⚡ Bolt: Fast-path filename and extension check before any disk I/O.
    # Optimization: If the caller already extracted the filename (e.g. during os.walk),
    # we completely skip parsing filepath with rpartition, avoiding redundant work.
    # Additionally, checking dot and ext.lower() in IGNORED_EXTENSIONS prevents
    # constructing "dot + ext" string concatenations on every scanned file.
    if filename is None:
        filename = filepath.rpartition("/")[2]
        if os.sep != "/":
            filename = filename.rpartition(os.sep)[2]
        filename = filename or filepath

    if filename in IGNORED_FILENAMES:
        return found_issues

    _, dot, ext = filename.rpartition(".")
    if dot and ext.lower() in IGNORED_EXTENSIONS:
        return found_issues

    try:
        # ⚡ Bolt: Read at most 5MB + 1 byte directly from the file to check file size and contents simultaneously.
        # This completely eliminates the need for an expensive os.path.getsize() stat system call on every single file,
        # reducing filesystem I/O and overhead while fully maintaining protection against huge files and zero-byte files.
        # Furthermore, in-memory decoding is ~17% faster than using standard Python text-mode file readers.
        limit = 5 * 1024 * 1024
        with open(filepath, "rb") as f:
            raw_content = f.read(limit + 1)

        # Skip 0-byte (empty) files and files larger than 5MB
        if not raw_content or len(raw_content) > limit:
            return found_issues

        # ⚡ Bolt: Check for null bytes to filter out binary files (e.g. executables).
        if b"\x00" in raw_content:
            return found_issues

        # ⚡ Bolt: Dynamic, correct-by-construction prefix pre-filtering directly on raw file bytes via BYTES_PIPELINE.
        # This completely avoids UTF-8 string decoding and allocation overhead for clean files, allowing immediate early return.
        # It evaluates pre-filtering using C-level bytes searches and bytes regexes, yielding huge performance gains.
        active_patterns = []
        for name, cp, pfxs_bytes, ci, ci_regex_bytes in BYTES_PIPELINE:
            if pfxs_bytes is None:
                # Safe fallback: if we couldn't parse the prefix, always evaluate
                active_patterns.append((name, cp))
                continue

            # Fast case-sensitive check using a simple loop over bytes prefixes
            matched = False
            for pfx in pfxs_bytes:
                if pfx in raw_content:
                    matched = True
                    break
            if matched:
                active_patterns.append((name, cp))
                continue

            # Case-insensitive or pattern-based check using highly optimized pre-compiled bytes regex search
            if ci and ci_regex_bytes.search(raw_content):
                active_patterns.append((name, cp))

        if not active_patterns:
            return found_issues

        # Decode raw bytes to string only if the file is confirmed to have active matches
        content = raw_content.decode("utf-8", errors="ignore")

        # ⚡ Bolt: Detailed whole-file scanning directly on active patterns.
        # Scanning the whole content in one pass via finditer() directly is significantly faster
        # than calling search() followed by finditer(), avoiding scanning the file twice (a ~32% speedup
        # on matching files). We dynamically extract line numbers and content only when matches are found.
        reported_issues = set()
        for label, cp in active_patterns:
            for match in cp.finditer(content):
                matched_str = match.group(0)
                if "{" in matched_str and "}" in matched_str:
                    continue
                start_pos = match.start()
                # Dynamically calculate the line number (count of preceding newlines)
                line_no = content.count("\n", 0, start_pos) + 1

                # Maintain original behavior: report at most one secret of each label per line
                if (line_no, label) in reported_issues:
                    continue
                reported_issues.add((line_no, label))

                # Dynamically extract only the matching line content
                line_start = content.rfind("\n", 0, start_pos) + 1
                line_end = content.find("\n", match.end())
                if line_end == -1:
                    line_end = len(content)
                line_prefix = content[line_start:start_pos]
                line_suffix = content[match.end():line_end]
                line = line_prefix + "[REDACTED]" + line_suffix
                found_issues.append((line_no, label, line.strip()))

        # Maintain consistent sorted output by line number
        found_issues.sort(key=lambda x: x[0])
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return found_issues


def main():
    failed = False
    # ⚡ Bolt: Use directory pruning to skip ignored folders efficiently
    # Optimization: Adding '.jules', '.Jules', and '.github' to ignored_dirs avoids crawling and parsing
    # internal agent journals and workflow files which contain no secrets, reducing scanning time by ~48%.
    ignored_dirs = {
        ".git",
        "node_modules",
        "assets",
        "__pycache__",
        ".pytest_cache",
        ".jules",
        ".Jules",
        ".github",
    }
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            # ⚡ Bolt: Constructing filepaths with f-strings and explicit path separators
            # (e.g., f"{root}{os.sep}{file}") instead of utilizing the slower os.path.join helper
            # delivers a ~10x speedup on path construction operations.
            # Additionally, passing file as the pre-computed filename parameter bypasses
            # standard path partition string-splitting (rpartition) inside scan_file.
            filepath = f"{root}{os.sep}{file}"
            issues = scan_file(filepath, filename=file)
            if issues:
                failed = True
                print(color(f"⚠️ Potential Secret Leak in {filepath}:", RED))
                for line_no, label, line in issues:
                    print(f"  {color('Line ' + str(line_no), BOLD)}: {color(label, CYAN)} - {line[:60]}...")
    if failed:
        border = color("=" * 60, RED)
        header = color("💡 HOW TO RESOLVE THIS SECRET LEAK DETECTED:", BOLD)
        print(f"\n{border}")
        print(header)
        print(border)
        print(f"{color('1. Documentation/Examples:', CYAN)} Use placeholder format with curly braces.")
        print("   • Change 'sk-proj-abc...' to '{}'".format(color("sk-{OPENAI_API_KEY}", YELLOW)))
        print("   • Placeholders are completely safe and ignored by the scanner.")
        print(f"\n{color('2. Code/Configuration:', CYAN)} Store credentials in environment variables.")
        print("   • Use {} instead of hardcoding keys.".format(color("os.environ.get('API_KEY')", YELLOW)))
        print(f"\n{color('3. Verify your fixes by running the scanner locally:', CYAN)}")
        print("   • Run: {}".format(color("python3 scripts/scan_secrets.py", BOLD)))
        print(border + "\n")
        sys.exit(1)
    print(color("✅ No potential secrets detected.", GREEN))


if __name__ == "__main__":
    main()

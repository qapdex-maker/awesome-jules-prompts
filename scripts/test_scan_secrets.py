import os
import tempfile
import pytest
from scripts.scan_secrets import scan_file, PATTERNS

def create_temp_file(content):
    fd, path = tempfile.mkstemp(suffix=".txt")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    except Exception:
        os.close(fd)
        raise

@pytest.fixture
def run_scan():
    temp_files = []
    def _scan(content):
        path = create_temp_file(content)
        temp_files.append(path)
        return scan_file(path)
    yield _scan
    for path in temp_files:
        try:
            os.remove(path)
        except OSError:
            pass

def test_clean_file(run_scan):
    content = "This is a clean file without any secrets."
    issues = run_scan(content)
    assert len(issues) == 0

def test_traditional_openai_key(run_scan):
    # 32 characters after sk- (alphanumeric only)
    # Concatenated to avoid triggering scanner on this test file
    content = "my_key = '" + "sk-" + "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "OpenAI API Key"

def test_modern_openai_key_with_hyphens(run_scan):
    # Modern sk-proj- key format with hyphens
    # Concatenated to avoid triggering scanner on this test file
    content = "openai_key = '" + "sk-" + "proj-abc123abc123abc123abc123abc123abc123abc123'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "OpenAI API Key"

def test_aws_access_key(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "aws_key = '" + "AKIA" + "1234567890ABCDEF'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "AWS Access Key"

def test_google_api_key(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "google_key = '" + "AIzaSy" + "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P67'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Google API Key"

def test_placeholder_ignored(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "openai_key = '" + "sk-" + "{OPENAI_API_KEY}'"
    issues = run_scan(content)
    assert len(issues) == 0

def test_multi_match_line_detects_real_secret(run_scan):
    # A placeholder followed by a real key on the same line
    # Concatenated to avoid triggering scanner on this test file
    content = "placeholder = '" + "sk-" + "{API_KEY}' and real = '" + "sk-" + "proj-abc123abc123abc123abc123abc123abc123abc123'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "OpenAI API Key"

def test_generic_token(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "api_key = '" + "some_random_high_" + "entropy_secret_key'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Generic Token"

def test_github_classic_token(run_scan):
    # ghp_ format, length of 40 total
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "ghp_" + "1234567890abcdefghijklmnopqrstuvwxyz12'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "GitHub Token"

def test_github_fine_grained_token(run_scan):
    # github_pat_ format
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "github_pat_" + "1234567890abcdefghijkl_1234567890abcdefghijklmnopqrstuvwx_1234567890'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "GitHub Token"

def test_github_placeholder_ignored(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "ghp_" + "{GITHUB_TOKEN}'"
    issues = run_scan(content)
    assert len(issues) == 0

def test_anthropic_api03_key(run_scan):
    # Anthropic api03 key format, sk-ant-api03- followed by 93 chars and AA
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "sk-ant-" + "api03-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrsAA'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Anthropic API Key"

def test_anthropic_admin01_key(run_scan):
    # Anthropic admin01 key format, sk-ant-admin01- followed by 93 chars and AA
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "sk-ant-" + "admin01-1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890abcdefghijklmnopqrsAA'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Anthropic API Key"

def test_anthropic_placeholder_ignored(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "sk-ant-" + "{ANTHROPIC_API_KEY}'"
    issues = run_scan(content)
    assert len(issues) == 0

def test_huggingface_token_34_chars(run_scan):
    # hf_ format with 34 characters (34 chars after hf_)
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "hf_" + "abcdefghijklmnopqrstuvwxyz12345678'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Hugging Face Token"

def test_huggingface_token_37_chars(run_scan):
    # hf_ format with 37 characters (37 chars after hf_)
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "hf_" + "abcdefghijklmnopqrstuvwxyz12345678901'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Hugging Face Token"

def test_huggingface_token_40_chars(run_scan):
    # hf_ format with 40 characters (40 chars after hf_)
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "hf_" + "abcdefghijklmnopqrstuvwxyz12345678901234'"
    issues = run_scan(content)
    assert len(issues) == 1
    assert issues[0][1] == "Hugging Face Token"

def test_huggingface_too_short_ignored(run_scan):
    # hf_ followed by 33 characters (below minimum 34) should be ignored
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "hf_" + "abcdefghijklmnopqrstuvwxyz1234567'"
    issues = run_scan(content)
    assert len(issues) == 0

def test_huggingface_placeholder_ignored(run_scan):
    # Concatenated to avoid triggering scanner on this test file
    content = "val = '" + "hf_" + "{HF_TOKEN}'"
    issues = run_scan(content)
    assert len(issues) == 0

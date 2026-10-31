"""Security utilities for input validation, archive safety, and secret redaction."""
import os
import re
import ipaddress
import zipfile
from urllib.parse import urlparse
from typing import Tuple, List

# Limits
MAX_UPLOAD_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
MAX_UNCOMPRESSED_SIZE_BYTES = 250 * 1024 * 1024  # 250 MB
MAX_FILES_COUNT = 2000
MAX_SOURCE_FILE_BYTES = 2 * 1024 * 1024  # 2 MB per file for static parsing

# Allowed file extensions for analysis
ANALYZABLE_EXTENSIONS = {
    ".py", ".java", ".cbl", ".cob", ".cpy", ".sql", ".js", ".jsx",
    ".ts", ".tsx", ".xml", ".wsdl", ".json", ".yaml", ".yml",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rb", ".php", ".sh"
}

GITHUB_URL_REGEX = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)

# Common secret patterns for redaction
SECRET_PATTERNS = [
    re.compile(r'(?i)(api[_-]?key|secret|token|password|auth[_-]?token|access[_-]?key|private[_-]?key)\s*[:=]\s*["\']([A-Za-z0-9_\-.~+/=]{8,})["\']'),
    re.compile(r'(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*'),
    re.compile(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC )?PRIVATE KEY-----'),
    re.compile(r'(?i)(AIza[0-9A-Za-z-_]{35})'),  # Google API key
    re.compile(r'(?i)(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})'),  # GitHub token
    re.compile(r'(?i)(AKIA[0-9A-Z]{16})'),  # AWS Access Key
]


def validate_github_url(url: str) -> Tuple[bool, str]:
    """Validate public GitHub URL and protect against SSRF and credential embedding."""
    if not url or not isinstance(url, str):
        return False, "Repository URL must be a non-empty string"

    url = url.strip()

    # Reject credentials in URL e.g. https://user:pass@github.com/...
    parsed = urlparse(url)
    if parsed.username or parsed.password:
        return False, "URLs with embedded credentials are not permitted"

    if parsed.scheme.lower() != "https":
        return False, "Only secure HTTPS GitHub URLs are accepted"

    if parsed.hostname and parsed.hostname.lower() != "github.com":
        return False, f"Host '{parsed.hostname}' is not supported. Only public GitHub repositories (github.com) are allowed."

    match = GITHUB_URL_REGEX.match(url)
    if not match:
        return False, "Invalid GitHub repository format. Expected: https://github.com/owner/repository"

    owner, repo = match.groups()
    if repo.endswith(".git"):
        repo = repo[:-4]

    # Check for reserved or local words
    if owner.lower() in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return False, "Invalid repository owner"

    return True, f"https://github.com/{owner}/{repo}.git"


def sanitize_analysis_id(analysis_id: str) -> bool:
    """Validate analysis ID format to prevent directory traversal or injection."""
    if not analysis_id or not isinstance(analysis_id, str):
        return False
    return bool(re.match(r"^[A-Za-z0-9_-]{3,64}$", analysis_id))


def safe_extract_zip(zip_path: str, extract_dir: str) -> Tuple[bool, str, int]:
    """
    Safely extract a ZIP archive protecting against:
    - Zip Slip / path traversal
    - Decompression bombs
    - Symlinks / special devices
    - Excessive file count
    """
    dest_dir = os.path.abspath(extract_dir)
    total_uncompressed_bytes = 0
    extracted_files_count = 0

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for info in zf.infolist():
                # Enforce file count limit
                extracted_files_count += 1
                if extracted_files_count > MAX_FILES_COUNT:
                    return False, f"Archive exceeds maximum file limit of {MAX_FILES_COUNT} files", 0

                # Check uncompressed size
                total_uncompressed_bytes += info.file_size
                if total_uncompressed_bytes > MAX_UNCOMPRESSED_SIZE_BYTES:
                    return False, f"Archive exceeds maximum uncompressed size of {MAX_UNCOMPRESSED_SIZE_BYTES // (1024*1024)} MB", 0

                # Path traversal / Zip Slip check
                target_path = os.path.abspath(os.path.join(dest_dir, info.filename))
                if not (target_path == dest_dir or target_path.startswith(dest_dir + os.sep)):
                    return False, f"Illegal file path in archive: {info.filename}", 0

                # Check for symlinks (external_attr for unix symlink is 0o120000 << 16)
                if (info.external_attr >> 16) & 0o120000 == 0o120000:
                    # Skip symlink to prevent symlink traversal attacks
                    continue

                # Safe to extract this item
                zf.extract(info, dest_dir)

        return True, "Extracted successfully", extracted_files_count

    except zipfile.BadZipFile:
        return False, "Invalid or corrupted ZIP archive", 0
    except Exception as e:
        return False, f"Archive extraction failed: {str(e)}", 0


def redact_secrets(text: str) -> str:
    """Redact known secret patterns from source snippets before external AI processing."""
    if not text:
        return ""

    sanitized = text
    # Key-value secret patterns with capture group for the key
    kv_pattern = re.compile(r'(?i)(api[_-]?key|secret|token|password|auth[_-]?token|access[_-]?key|private[_-]?key)\s*[:=]\s*["\']([^"\']+)["\']')
    sanitized = kv_pattern.sub(r'\1: "[REDACTED_SECRET]"', sanitized)

    # Bearer tokens
    sanitized = re.sub(r'(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*', 'Bearer [REDACTED_TOKEN]', sanitized)

    # Private key blocks
    sanitized = re.sub(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC )?PRIVATE KEY-----', '[REDACTED_PRIVATE_KEY]', sanitized)

    # Known token formats
    sanitized = re.sub(r'(?i)AIza[0-9A-Za-z-_]{35}', '[REDACTED_GOOGLE_KEY]', sanitized)
    sanitized = re.sub(r'(?i)ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}', '[REDACTED_GITHUB_TOKEN]', sanitized)
    sanitized = re.sub(r'(?i)AKIA[0-9A-Z]{16}', '[REDACTED_AWS_KEY]', sanitized)

    return sanitized

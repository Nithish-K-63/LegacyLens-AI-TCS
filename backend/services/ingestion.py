"""Repository and archive ingestion service."""
import os
import shutil
import stat
import tempfile
from typing import List, Dict, Any, Tuple
import git
from backend.services.security import safe_extract_zip, MAX_UPLOAD_SIZE_BYTES, ANALYZABLE_EXTENSIONS

# Directories and files to ignore during ingestion
IGNORED_DIRS = {
    ".git", ".svn", ".hg", "node_modules", "vendor", "__pycache__",
    ".pytest_cache", ".venv", "venv", "env", ".idea", ".vscode",
    "dist", "build", "target", "out", ".gradle", "bin", "obj"
}

IGNORED_EXTENSIONS = {
    ".pyc", ".pyo", ".class", ".o", ".obj", ".exe", ".dll", ".so",
    ".dylib", ".zip", ".tar", ".gz", ".png", ".jpg", ".jpeg", ".gif",
    ".ico", ".svg", ".woff", ".woff2", ".ttf", ".eot", ".mp3", ".mp4",
    ".pdf", ".lock"
}


def remove_readonly(func, path, exc_info):
    """Error handler for Windows git repo file removal (handles read-only .git files)."""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def detect_project_root(extracted_dir: str) -> str:
    """
    If extracted_dir contains only a single wrapper directory (e.g. repo-master/),
    unwrap and return that inner directory as the real project root.
    """
    try:
        entries = [
            e for e in os.listdir(extracted_dir)
            if not e.startswith(".") and e != "__MACOSX"
        ]
        if len(entries) == 1:
            candidate = os.path.join(extracted_dir, entries[0])
            if os.path.isdir(candidate):
                return candidate
    except Exception:
        pass
    return extracted_dir


def cleanup_directory(path: str) -> None:
    """Safely delete temporary directory and its contents."""
    if not path or not os.path.exists(path):
        return
    target = path
    parent = os.path.dirname(os.path.abspath(path))
    if "legacylens_" in os.path.basename(parent):
        target = parent
    try:
        shutil.rmtree(target, onerror=remove_readonly)
    except Exception:
        try:
            shutil.rmtree(target, ignore_errors=True)
        except Exception:
            pass


def clone_github_repository(repo_url: str, branch: str = None) -> Tuple[bool, str, str]:
    """
    Shallow-clone a GitHub repository into a temporary directory.
    Returns: (success, temp_dir_path, error_message)
    """
    temp_dir = tempfile.mkdtemp(prefix="legacylens_repo_")
    try:
        clone_kwargs = {
            "depth": 1,
            "single_branch": True
        }
        if branch:
            clone_kwargs["branch"] = branch

        git.Repo.clone_from(repo_url, temp_dir, **clone_kwargs)
        return True, temp_dir, ""
    except Exception as e:
        cleanup_directory(temp_dir)
        err = str(e)
        if "Repository not found" in err:
            err = "Repository not found or is private"
        elif "could not read Username" in err:
            err = "Authentication required or repository does not exist"
        return False, "", f"Git clone failed: {err}"


def ingest_zip_archive(zip_path: str) -> Tuple[bool, str, str, int]:
    """
    Safely unpack a ZIP archive into a temporary directory.
    Auto-detects and unwraps nested wrapper directory if present.
    Returns: (success, real_root_path, message, file_count)
    """
    temp_dir = tempfile.mkdtemp(prefix="legacylens_zip_")
    success, msg, file_count = safe_extract_zip(zip_path, temp_dir)
    if not success:
        cleanup_directory(temp_dir)
        return False, "", msg, 0
    real_root = detect_project_root(temp_dir)
    return True, real_root, "Extracted", file_count


def scan_file_inventory(root_dir: str) -> List[Dict[str, Any]]:
    """
    Scan root directory and collect inventory of source files.
    Returns list of dicts: {path, relative_path, extension, size_bytes, language}
    """
    inventory = []
    root_abs = os.path.abspath(root_dir)

    for current_root, dirs, files in os.walk(root_abs):
        # Modify dirs in-place to avoid descending into ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]

        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in IGNORED_EXTENSIONS or filename.startswith("."):
                continue

            full_path = os.path.join(current_root, filename)
            rel_path = os.path.relpath(full_path, root_abs).replace("\\", "/")

            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0

            lang = detect_language(filename, ext)
            inventory.append({
                "path": full_path,
                "relative_path": rel_path,
                "extension": ext,
                "size_bytes": size,
                "language": lang,
                "is_analyzable": ext in ANALYZABLE_EXTENSIONS
            })

    return inventory


def detect_language(filename: str, ext: str) -> str:
    """Map file extension/name to programming language."""
    ext_map = {
        ".py": "Python",
        ".java": "Java",
        ".cbl": "COBOL",
        ".cob": "COBOL",
        ".cpy": "COBOL",
        ".sql": "SQL",
        ".js": "JavaScript",
        ".jsx": "JavaScript (React)",
        ".ts": "TypeScript",
        ".tsx": "TypeScript (React)",
        ".xml": "XML",
        ".wsdl": "WSDL",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".c": "C",
        ".cpp": "C++",
        ".h": "C/C++ Header",
        ".hpp": "C++ Header",
        ".cs": "C#",
        ".go": "Go",
        ".rb": "Ruby",
        ".php": "PHP",
        ".sh": "Shell",
        ".properties": "Config",
        ".ini": "Config",
        ".conf": "Config",
        ".md": "Markdown",
        ".txt": "Text"
    }
    return ext_map.get(ext.lower(), "Other")


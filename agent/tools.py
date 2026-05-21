# import pathlib
# import subprocess
# from typing import Tuple
#
# from langchain_core.tools import tool
#
# PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"
#
#
# def safe_path_for_project(path: str) -> pathlib.Path:
#     p = (PROJECT_ROOT / path).resolve()
#     if PROJECT_ROOT.resolve() not in p.parents and PROJECT_ROOT.resolve() != p.parent and PROJECT_ROOT.resolve() != p:
#         raise ValueError("Attempt to write outside project root")
#     return p
#
#
# @tool
# def write_file(path: str, content: str) -> str:
#     """Writes content to a file at the specified path within the project root."""
#     p = safe_path_for_project(path)
#     p.parent.mkdir(parents=True, exist_ok=True)
#     with open(p, "w", encoding="utf-8") as f:
#         f.write(content)
#     return f"WROTE:{p}"
#
#
# @tool
# def read_file(path: str) -> str:
#     """Reads content from a file at the specified path within the project root."""
#     p = safe_path_for_project(path)
#     if not p.exists():
#         return ""
#     with open(p, "r", encoding="utf-8") as f:
#         return f.read()
#
#
# @tool
# def get_current_directory() -> str:
#     """Returns the current working directory."""
#     return str(PROJECT_ROOT)
#
#
# @tool
# def list_files(directory: str = ".") -> str:
#     """Lists all files in the specified directory within the project root."""
#     p = safe_path_for_project(directory)
#     if not p.is_dir():
#         return f"ERROR: {p} is not a directory"
#     files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
#     return "\n".join(files) if files else "No files found."
#
# @tool
# def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
#     """Runs a shell command in the specified directory and returns the result."""
#     cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
#     res = subprocess.run(cmd, shell=True, cwd=str(cwd_dir), capture_output=True, text=True, timeout=timeout)
#     return res.returncode, res.stdout, res.stderr
#
#
# def init_project_root():
#     PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
#     return str(PROJECT_ROOT)

import pathlib
from langchain_core.tools import tool
import subprocess
from typing import Tuple


# 1. Always resolve the root immediately to handle casing/symlinks
PROJECT_ROOT = (pathlib.Path.cwd() / "generated_project").resolve()


def safe_path_for_project(path_str: str) -> pathlib.Path:
    # 2. Convert to Path and strip leading slashes/backslashes
    # This prevents 'PROJECT_ROOT / "/etc/passwd"' from becoming '/etc/passwd'
    clean_path = str(path_str).lstrip("\\/")

    # 3. Join and resolve to get the actual final location
    requested_path = (PROJECT_ROOT / clean_path).resolve()

    # 4. Use is_relative_to for a cleaner, more reliable check
    # If on Python < 3.9, use: PROJECT_ROOT in requested_path.parents or PROJECT_ROOT == requested_path
    try:
        requested_path.relative_to(PROJECT_ROOT)
    except ValueError:
        raise ValueError(f"Attempt to access path outside project root: {requested_path}")

    return requested_path


@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the specified path within the project root."""
    try:
        p = safe_path_for_project(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)
        return f"WROTE: {p.relative_to(PROJECT_ROOT)}"
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def read_file(path: str) -> str:
    """Reads content from a file at the specified path within the project root."""
    try:
        p = safe_path_for_project(path)
        if not p.exists():
            return "ERROR: File does not exist."
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR: {str(e)}"


@tool
def list_files(directory: str = ".") -> str:
    """Lists all files in the specified directory within the project root."""
    try:
        p = safe_path_for_project(directory)
        if not p.is_dir():
            return f"ERROR: {directory} is not a directory"

        # Get all files and make them relative to root for the LLM to see clearly
        files = [str(f.relative_to(PROJECT_ROOT)) for f in p.rglob("*") if f.is_file()]
        return "\n".join(files) if files else "No files found."
    except Exception as e:
        return f"ERROR: {str(e)}"

@tool
def get_current_directory() -> str:
    """Returns the absolute path to the project root directory."""
    return str(PROJECT_ROOT)

@tool
def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    """Runs a shell command in the specified directory and returns the result."""
    cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
    res = subprocess.run(cmd, shell=True, cwd=str(cwd_dir), capture_output=True, text=True, timeout=timeout)
    return res.returncode, res.stdout, res.stderr
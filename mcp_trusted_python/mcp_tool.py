import asyncio
import json
import os
import tempfile
from pathlib import Path

from mcp.server.fastmcp import FastMCP, Context

mcp = FastMCP("Python MCP Server")

# Shared session dir
SESSION_DIR_ROOT = tempfile.mkdtemp(prefix="mcp_session_root_")


def create_session_dir() -> str:
    """Create isolated session directory for each operation"""
    path = tempfile.mkdtemp(prefix="session_", dir=SESSION_DIR_ROOT)
    return path


@mcp.tool()
async def run_python(code: str, filename: str = "script.py", ctx: Context = None) -> dict:
    """
    Execute Python code in an isolated environment with security restrictions.
    
    Args:
        code: The Python code to execute
        filename: Name for the temporary file (default: script.py)
        ctx: MCP context for logging
    
    Returns:
        dict with stdout, stderr, and returncode
    """
    session_dir = create_session_dir()
    file_path = os.path.join(session_dir, filename)
    
    # Wrap code with restricted execution environment
    restricted_code = f'''
import sys
import builtins

# Block dangerous imports
BLOCKED_MODULES = {{
    'urllib', 'urllib.request', 'urllib3', 'requests', 'http', 'httpx',
    'socket', 'ftplib', 'telnetlib', 'smtplib', 'poplib', 'imaplib',
    'subprocess', 'os.system', 'pty', 'commands',
    'pickle', 'shelve', 'marshal',  # unsafe deserialization
}}

original_import = builtins.__import__

def safe_import(name, *args, **kwargs):
    base_module = name.split('.')[0]
    if base_module in BLOCKED_MODULES:
        raise ImportError(f"Import of '{{name}}' is blocked for security reasons")
    return original_import(name, *args, **kwargs)

builtins.__import__ = safe_import

# Remove dangerous builtins
for attr in ['eval', 'exec', 'compile', '__import__']:
    if attr in dir(builtins) and attr != '__import__':
        delattr(builtins, attr)

# User code starts here
{code}
'''
    
    # Write wrapped code to file
    Path(file_path).write_text(restricted_code)
    
    if ctx:
        ctx.debug(f"Running python file: {file_path}")
    
    # Run with timeout to prevent infinite loops
    proc = await asyncio.create_subprocess_exec(
        "python3", file_path,
        cwd=session_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30.0)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return {
            "stdout": "",
            "stderr": "Execution timeout (30 seconds exceeded)",
            "returncode": -1,
            "session_dir": session_dir
        }
    
    return {
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "returncode": proc.returncode,
        "session_dir": session_dir
    }


@mcp.tool()
async def check_python(code: str, filename: str = "script.py", ctx: Context = None) -> dict:
    """
    Run linting and type checking on Python code.
    
    Args:
        code: The Python code to check
        filename: Name for the temporary file (default: script.py)
        ctx: MCP context for logging
    
    Returns:
        dict with ruff linting results and type checking results
    """
    session_dir = create_session_dir()
    file_path = os.path.join(session_dir, filename)
    
    # Write code to file
    Path(file_path).write_text(code)

    # Run ruff lint
    ruff_proc = await asyncio.create_subprocess_exec(
        "ruff", "check", "--output-format", "json", file_path,
        cwd=session_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    ruff_out, ruff_err = await ruff_proc.communicate()
    try:
        ruff_json = json.loads(ruff_out.decode()) if ruff_out else []
    except json.JSONDecodeError:
        ruff_json = []

    # Run type check 
    type_proc = await asyncio.create_subprocess_exec(
        "python3", "-m", "ty", file_path,
        cwd=session_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    type_out, type_err = await type_proc.communicate()

    return {
        "ruff_issues": ruff_json,
        "ruff_stderr": ruff_err.decode(),
        "type_check_output": type_out.decode(),
        "type_check_stderr": type_err.decode(),
        "type_check_returncode": type_proc.returncode,
        "session_dir": session_dir
    }


@mcp.tool()
async def fix_python(code: str, filename: str = "script.py", ctx: Context = None) -> dict:
    """
    Auto-fix Python code issues using ruff.
    
    Args:
        code: The Python code to fix
        filename: Name for the temporary file (default: script.py)
        ctx: MCP context for logging
    
    Returns:
        dict with fixed code and fix results
    """
    session_dir = create_session_dir()
    file_path = os.path.join(session_dir, filename)
    
    # Write code to file
    Path(file_path).write_text(code)

    proc = await asyncio.create_subprocess_exec(
        "ruff", "check", "--fix", file_path,
        cwd=session_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    
    # Read the fixed code
    fixed_code = Path(file_path).read_text()
    
    return {
        "fixed_code": fixed_code,
        "stdout": stdout.decode(),
        "stderr": stderr.decode(),
        "returncode": proc.returncode,
        "session_dir": session_dir
    }


@mcp.tool()
async def security_scan(code: str, filename: str = "script.py", ctx: Context = None) -> dict:
    """
    Run security scanning on Python code using bandit.
    
    Args:
        code: The Python code to scan
        filename: Name for the temporary file (default: script.py)
        ctx: MCP context for logging
    
    Returns:
        dict with bandit security scan results
    """
    session_dir = create_session_dir()
    file_path = os.path.join(session_dir, filename)
    
    # Write code to file
    Path(file_path).write_text(code)

    proc = await asyncio.create_subprocess_exec(
        "bandit", "-r", file_path, "-f", "json",
        cwd=session_dir,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await proc.communicate()
    try:
        bandit_json = json.loads(out.decode()) if out else {}
    except json.JSONDecodeError:
        bandit_json = {}

    return {
        "security_issues": bandit_json,
        "bandit_stderr": err.decode(),
        "bandit_returncode": proc.returncode,
        "session_dir": session_dir
    }


@mcp.tool()
async def list_installed_packages(ctx: Context = None) -> dict:
    """
    List all Python packages installed via pip.
    
    Returns:
        dict with list of installed packages and their versions
    """
    proc = await asyncio.create_subprocess_exec(
        "pip", "list", "--format", "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    
    try:
        packages = json.loads(stdout.decode()) if stdout else []
        # Format as a more readable dict
        package_dict = {pkg["name"]: pkg["version"] for pkg in packages}
        return {
            "packages": package_dict,
            "count": len(package_dict),
            "stderr": stderr.decode(),
            "returncode": proc.returncode
        }
    except json.JSONDecodeError:
        return {
            "packages": {},
            "count": 0,
            "stderr": stderr.decode() + "\nFailed to parse pip output",
            "returncode": proc.returncode
        }

def main():
    # Use stdio transport for Docker stdin/stdout communication
    mcp.run(transport="streamable-http")  # Defaults to stdio transport

if __name__ == "__main__":
    main()


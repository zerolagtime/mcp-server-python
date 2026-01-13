# Python MCP Tool

A Minimal Compute Platform (MCP) tool for **continue.dev** plugin in VSCode to run Python scripts, perform linting (using `ruff`), type checking (using `ty` from astral-sh), and security scanning (using `bandit`).

## Features

- Runs Python 3.11 code in isolation inside a Docker container.
- Checks Python code style and lint issues using `ruff`.
- Checks for type errors using `ty`.
- Performs security analysis using `bandit`.
- Uses isolated temporary directories for each session for cache and file management.
- Runs entirely inside a Docker container to ensure sandboxing and prevent unauthorized filesystem access.

## Requirements

- Docker installed and running on your machine.
- VSCode with the continue.dev extension.

## Building the Docker Image

To build the Docker image, run the following in your project root:

```bash
docker build -t python-mcp .
```

Alternatively, you can use the VSCode task:

1. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on Mac).
2. Run `Tasks: Run Build Task`.
3. Select `Build Python MCP Docker Image`.

## Using in continue.dev

The MCP tool is configured in `continue.dev.json`:

```json
{
  "name": "Python MCP",
  "run": {
    "cmd": ["docker", "run", "--rm", "-i", "-v", "${workspaceFolder}:/workspace", "python-mcp"],
    "stdin": true,
    "stdout": true,
    "stderr": true
  },
  "languages": ["python"],
  "description": "Run python code, lint, type check and security scan in isolated Docker container."
}
```

Make sure to build the Docker image first.

## Using the MCP Tool

The tool reads JSON requests on standard input and outputs JSON responses on standard output.

Example request to run Python script:

```json
{
  "action": "run_python",
  "path": "script.py",
  "content": "print('Hello world')\n"
}
```

Example request to lint and type check:

```json
{
  "action": "check_python",
  "path": "script.py",
  "content": "def foo(x: int) -> str:\n    return str(x)\n"
}
```

Example request for security scan:

```json
{
  "action": "security_scan",
  "path": "script.py",
  "content": "import os\nprint(os.listdir())\n"
}
```

The tool handles cache isolation per session by creating temporary directories.

## Notes

- The container runs as a non-root user for safety.
- Cache is cleared at the start of each session to prevent interference.
- The tool relies on the following Python tools installed inside the container:
  - `ruff` for linting
  - `bandit` for security scanning
- 
## License

MIT

## Sample `~/.continue/rules/python-rule.md`

```md
# Python Development Rules

## Test-Driven Development
- Write tests FIRST before implementation code
- Use `list_installed_packages()` to check available testing frameworks (pytest recommended)
- Run tests with `run_python()` to verify behavior before suggesting code
- Aim for >80% code coverage on business logic

## Code Quality & Validation
- Always `check_python()` and `security_scan()` before presenting code
- Use type hints for all function signatures (Python 3.11+)
- Keep cyclomatic complexity ≤3 per function (max 3 decision points/branches)
- Extract complex logic into well-named helper functions
- Write Pythonic, idiomatic code when it improves clarity

## SOLID Principles
- **Single Responsibility**: One function = one clear purpose
- **Open/Closed**: Use protocols/ABC for extensibility
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Small, focused interfaces over large ones
- **Dependency Inversion**: Depend on abstractions (protocols), inject dependencies

## Security & Configuration
- Use `python-dotenv` for sensitive values, never hardcode secrets
- Use stdlib `hashlib` and `secrets` for cryptography, avoid third-party crypto libs
- Validate all external inputs with type hints + runtime validation (pydantic recommended)

## Architecture Patterns
- Separate concerns: handlers → services → repositories
- Use dataclasses/pydantic models for data structures
- Implement error handling at boundaries with custom exceptions
- Document public APIs with docstrings (Google/NumPy style)
- Prefer composition over inheritance

## Workflow
1. Query `list_installed_packages()` to verify available dependencies
2. Write failing test
3. Implement minimal code to pass test
4. Run `check_python()` and `security_scan()`
5. Refactor while keeping tests green
6. Present validated, tested code
```
# Trusted Python MCP Tool

A Minimal Compute Platform (MCP) tool for **continue.dev** plugin in VSCode to run Python scripts, perform linting (using `ruff`), type checking (using `ty` from astral-sh), and security scanning (using `bandit`). It should work just fine with other tools

## Features

- Runs Python 3.11 code in isolation inside a Docker container.
- Checks Python code style and lint issues using `ruff`.
- Checks for type errors using `ty`.
- Performs security analysis using `bandit`.
- Uses isolated temporary directories for each session for cache and file management.
- Runs entirely inside a Docker container to ensure sandboxing and prevent unauthorized filesystem access.

## Quickstart

Install `uvx`. Administrative privileges are not required, but you will need to permanents add it to your path (e.g `~/.local/bin`)

Use as-is with `uvx mcp-trusted-python`. 

If extra libraries should always be available to the agent, then put them in a requirements file (e.g `requirements-science.txt`). Then, substituting your preferred Python interpreter,

```sh
uvx create --python python3.11 mcp-trusted-python
uvx shell mcp-trusted-python
uv pip install mcp-trusted-python
uv pip install -r requirements-science.txt
```

## License

MIT

# Python Development Rules
Add these to your tool's rules to include with `*.py` files. For continue.dev, these go in `~/.continue/rules/trusted-python-rules.md`. The rules

```md
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
- Web applications always include CORS support and disable debugging at run time

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
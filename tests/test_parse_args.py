import sys
import pytest

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # Always clear env before/after each test
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)

def test_parse_args_default(monkeypatch):
    from mcp_trusted_python import parse_args
    sys_argv = ["prog"]
    monkeypatch.setattr(sys, "argv", sys_argv)
    # No env, no CLI: uses default 'stdio'
    opts = parse_args.parse_args()
    assert opts["transport"] == "stdio"

def test_parse_args_env(monkeypatch):
    from mcp_trusted_python import parse_args
    sys_argv = ["prog"]
    monkeypatch.setattr(sys, "argv", sys_argv)
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    opts = parse_args.parse_args()
    assert opts["transport"] == "streamable-http"

def test_parse_args_cli(monkeypatch):
    from mcp_trusted_python import parse_args
    sys_argv = ["prog", "--transport", "foo"]
    monkeypatch.setattr(sys, "argv", sys_argv)
    monkeypatch.setenv("MCP_TRANSPORT", "something-else")
    opts = parse_args.parse_args(default_transport="xyz")
    assert opts["transport"] == "foo"

def test_parse_args_empty_env(monkeypatch):
    from mcp_trusted_python import parse_args
    sys_argv = ["prog"]
    monkeypatch.setattr(sys, "argv", sys_argv)
    monkeypatch.setenv("MCP_TRANSPORT", "")
    opts = parse_args.parse_args(default_transport="fallback")
    assert opts["transport"] == "fallback"
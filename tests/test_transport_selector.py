import sys
import pytest

@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)

def test_transport_selector_default(monkeypatch):
    from mcp_trusted_python import transport_selector
    monkeypatch.setattr(sys, "argv", ["prog"])
    result = transport_selector.select_transport(default="stdio")
    assert result == "stdio"

def test_transport_selector_env(monkeypatch):
    from mcp_trusted_python import transport_selector
    monkeypatch.setattr(sys, "argv", ["prog"])
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")
    result = transport_selector.select_transport(default="other")
    assert result == "streamable-http"

def test_transport_selector_cli(monkeypatch):
    from mcp_trusted_python import transport_selector
    monkeypatch.setattr(sys, "argv", ["prog", "--transport", "x"])
    monkeypatch.setenv("MCP_TRANSPORT", "y")
    result = transport_selector.select_transport(default="other")
    assert result == "x"

def test_transport_selector_priority(monkeypatch):
    from mcp_trusted_python import transport_selector
    # CLI wins over env, env wins over default
    monkeypatch.setattr(sys, "argv", ["prog", "--transport", "from_cli"])
    monkeypatch.setenv("MCP_TRANSPORT", "from_env")
    assert transport_selector.select_transport("zzz") == "from_cli"
    monkeypatch.setattr(sys, "argv", ["prog"])
    assert transport_selector.select_transport("zzz") == "from_env"
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    assert transport_selector.select_transport("zzz") == "zzz"
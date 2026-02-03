import pytest
from mcp_trusted_python import mcp_tool

@pytest.mark.asyncio
async def test_run_python_happy():
    code = "print('hello')"
    result = await mcp_tool.run_python(code)
    assert result["returncode"] == 0
    assert "hello" in result["stdout"]

@pytest.mark.asyncio
async def test_check_python_happy():
    code = "a = 123\nprint(a)\n"
    result = await mcp_tool.check_python(code)
    assert isinstance(result["ruff_issues"], list)
    assert result["type_check_returncode"] == 0

@pytest.mark.asyncio
async def test_fix_python_happy():
    code = (
        'foo = {\n'
        '"bar": 1,\n'
        '"baz": 2\n'
        '}\n'
    )
    result = await mcp_tool.fix_python(code)
    assert "fixed_code" in result
    # Ruff adds trailing comma, but leaves final newline, and keeps keys double-quoted
    expected_fixed = (
        'foo = {\n'
        '"bar": 1,\n'
        '"baz": 2,\n'
        '}\n'
    )
    assert result["fixed_code"] == expected_fixed

@pytest.mark.asyncio
async def test_security_scan_happy():
    code = "print('safe')"
    result = await mcp_tool.security_scan(code)
    assert "security_issues" in result
    assert isinstance(result["security_issues"], list)
    assert result["ruff_returncode"] in (0, 1)  # Ruff returns 1 if any lint errors found
    # For safe code, expect no issues
    assert result["security_issues"] == []
    
@pytest.mark.asyncio
async def test_list_installed_packages_happy():
    result = await mcp_tool.list_installed_packages()
    assert "packages" in result
    assert isinstance(result["packages"], dict)
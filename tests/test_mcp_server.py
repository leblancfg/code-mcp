import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import Tool, TextContent
from src.code_mcp.server import CodeInterpreterServer


@pytest.fixture
def server():
    return CodeInterpreterServer()


@pytest.fixture
def mock_gcf_response():
    return {
        "stdout": "Hello, World!",
        "stderr": "",
        "exitCode": 0
    }


async def test_server_initialization(server):
    assert server.name == "code-interpreter"
    assert hasattr(server, 'run_code')


async def test_list_tools(server):
    tools = await server.list_tools()
    assert len(tools) == 1
    assert tools[0].name == "run_code"
    assert tools[0].description == "Execute code in a sandboxed environment"
    assert "code" in tools[0].inputSchema["properties"]
    assert "language" in tools[0].inputSchema["properties"]


async def test_run_code_tool_python(server, mock_gcf_response):
    with patch('src.code_mcp.server.CodeInterpreterServer._call_gcf', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_gcf_response
        
        result = await server.run_code(
            code="print('Hello, World!')",
            language="python"
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "Hello, World!"
        
        mock_call.assert_called_once_with(
            "print('Hello, World!')",
            "python"
        )


async def test_run_code_tool_javascript(server, mock_gcf_response):
    mock_gcf_response["stdout"] = "42"
    
    with patch('src.code_mcp.server.CodeInterpreterServer._call_gcf', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_gcf_response
        
        result = await server.run_code(
            code="console.log(6 * 7)",
            language="javascript"
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "42"
        
        mock_call.assert_called_once_with(
            "console.log(6 * 7)",
            "javascript"
        )


async def test_run_code_with_error(server):
    error_response = {
        "stdout": "",
        "stderr": "SyntaxError: invalid syntax",
        "exitCode": 1
    }
    
    with patch('src.code_mcp.server.CodeInterpreterServer._call_gcf', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = error_response
        
        result = await server.run_code(
            code="print('unclosed",
            language="python"
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "SyntaxError: invalid syntax" in result[0].text
        assert "Exit code: 1" in result[0].text


async def test_run_code_gcf_failure(server):
    with patch('src.code_mcp.server.CodeInterpreterServer._call_gcf', new_callable=AsyncMock) as mock_call:
        mock_call.side_effect = Exception("GCF connection failed")
        
        with pytest.raises(Exception) as exc_info:
            await server.run_code(
                code="print('test')",
                language="python"
            )
        
        assert "GCF connection failed" in str(exc_info.value)


async def test_handle_call_tool(server, mock_gcf_response):
    with patch('src.code_mcp.server.CodeInterpreterServer._call_gcf', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_gcf_response
        
        result = await server.handle_call_tool(
            "run_code",
            arguments={
                "code": "print('Hello, World!')",
                "language": "python"
            }
        )
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "Hello, World!"


async def test_handle_call_tool_invalid_tool(server):
    with pytest.raises(ValueError) as exc_info:
        await server.handle_call_tool(
            "invalid_tool",
            arguments={}
        )
    
    assert "Unknown tool: invalid_tool" in str(exc_info.value)
import os
import json
import asyncio
import logging
from typing import Any, Sequence
import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, CallToolRequest, ListToolsRequest

logger = logging.getLogger(__name__)


class CodeInterpreterServer(Server):
    def __init__(self):
        super().__init__("code-interpreter")
        self.gcf_url = os.getenv("GCF_URL")
        if not self.gcf_url:
            logger.warning("GCF_URL not set, will need to be configured")
    
    async def list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="run_code",
                description="Execute code in a sandboxed environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code to execute"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language (python, javascript, bash)",
                            "enum": ["python", "javascript", "bash"]
                        }
                    },
                    "required": ["code", "language"]
                }
            )
        ]
    
    async def handle_call_tool(
        self, name: str, arguments: dict[str, Any] | None
    ) -> Sequence[TextContent]:
        if name != "run_code":
            raise ValueError(f"Unknown tool: {name}")
        
        if not arguments:
            raise ValueError("Missing arguments")
        
        code = arguments.get("code")
        language = arguments.get("language")
        
        if not code or not language:
            raise ValueError("Missing required arguments: code and language")
        
        result = await self.run_code(code, language)
        return result
    
    async def run_code(self, code: str, language: str) -> list[TextContent]:
        response = await self._call_gcf(code, language)
        
        stdout = response.get("stdout", "")
        stderr = response.get("stderr", "")
        exit_code = response.get("exitCode", 0)
        
        output = stdout
        if stderr:
            output += f"\n\nErrors:\n{stderr}"
        if exit_code != 0:
            output += f"\n\nExit code: {exit_code}"
        
        return [TextContent(type="text", text=output.strip())]
    
    async def _call_gcf(self, code: str, language: str) -> dict:
        loop = asyncio.get_event_loop()
        
        def make_request():
            return requests.post(
                self.gcf_url,
                json={"code": code, "language": language},
                timeout=35
            )
        
        response = await loop.run_in_executor(None, make_request)
        response.raise_for_status()
        return response.json()
    
    async def initialize(self, params: InitializationOptions) -> None:
        await super().initialize(params)
        
        if not self.gcf_url:
            from .gcf_deployer import GCFDeployer
            deployer = GCFDeployer()
            deployment = deployer.deploy()
            if deployment["success"]:
                self.gcf_url = deployment["function_url"]
                logger.info(f"GCF deployed at: {self.gcf_url}")
            else:
                logger.error("Failed to deploy GCF")


def create_server():
    return CodeInterpreterServer()


async def main():
    server = create_server()
    
    from mcp.server.stdio import StdioServerTransport
    transport = StdioServerTransport()
    await server.connect(transport)
    
    # Keep server running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
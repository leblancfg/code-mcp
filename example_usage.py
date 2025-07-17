#!/usr/bin/env python
"""
Example demonstrating how to use the Code MCP server programmatically.

This shows how an AI agent would interact with the MCP server to execute code.
"""

import asyncio
import json
from mcp.client import ClientSession
from mcp.client.stdio import stdio_client


async def main():
    # Connect to the MCP server via stdio
    async with stdio_client() as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Example 1: Execute Python code
            print("\n--- Python Example ---")
            result = await session.call_tool(
                "run_code",
                arguments={
                    "code": "print('Hello from Python!')\nprint(2 + 2)",
                    "language": "python"
                }
            )
            print(f"Result: {result[0].text}")
            
            # Example 2: Execute JavaScript code
            print("\n--- JavaScript Example ---")
            result = await session.call_tool(
                "run_code",
                arguments={
                    "code": "console.log('Hello from JavaScript!');\nconsole.log(6 * 7);",
                    "language": "javascript"
                }
            )
            print(f"Result: {result[0].text}")
            
            # Example 3: Execute Bash code
            print("\n--- Bash Example ---")
            result = await session.call_tool(
                "run_code",
                arguments={
                    "code": "echo 'Hello from Bash!'\necho $((3 + 4))",
                    "language": "bash"
                }
            )
            print(f"Result: {result[0].text}")
            
            # Example 4: Handle errors
            print("\n--- Error Handling Example ---")
            result = await session.call_tool(
                "run_code",
                arguments={
                    "code": "print('Unclosed string",
                    "language": "python"
                }
            )
            print(f"Result: {result[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
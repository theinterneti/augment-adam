#!/usr/bin/env python3

import sys
from mcp.client.session import ClientSession

async def main():
    # Connect to the MCP server
    async with ClientSession("http://localhost:8082/mcp") as session:
        # Initialize the session
        await session.initialize()

        # List available tools
        tools = await session.list_tools()
        print(f"Available tools: {tools}")

        # Call the echo tool
        if "echo" in [tool.name for tool in tools]:
            result = await session.call_tool("echo", {"message": "Hello, MCP!"})
            print(f"Echo result: {result}")
        else:
            print("Echo tool not found")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

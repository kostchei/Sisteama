#!/usr/bin/env python3
"""
Entry point for running the TaleKeeper MCP server.
Use this script to start the server for testing with MCP clients.
"""

import asyncio
import sys
from pathlib import Path

# Add core directory to path
sys.path.append(str(Path(__file__).parent / "core"))

# Import FastMCP server from our mcp_server module
from mcp_server import mcp


async def main():
    """Run the MCP server"""
    # Use stdio transport for MCP communication
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(read_stream, write_stream)


if __name__ == "__main__":
    print("Starting TaleKeeper MCP Server...", file=sys.stderr)
    print("Available tools:", file=sys.stderr)
    print("- roll_d20: Roll d20 with modifiers and advantage", file=sys.stderr)
    print("- roll_damage: Roll damage dice", file=sys.stderr)
    print("- roll_attack: Complete attack with damage", file=sys.stderr)
    print("- create_character: Create D&D character", file=sys.stderr)
    print("- get_character: Get character info", file=sys.stderr)
    print("- damage_character: Apply damage", file=sys.stderr)
    print("- start_combat: Begin encounter", file=sys.stderr)
    print("- roll_saving_throw: Roll saves", file=sys.stderr)
    print("Use 'uv run mcp dev run_mcp_server.py' to test", file=sys.stderr)
    print("", file=sys.stderr)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server stopped.", file=sys.stderr)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

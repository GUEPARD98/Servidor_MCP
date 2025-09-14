#!/usr/bin/env python3
"""
Test script for the Dice Roller MCP Server
"""
import asyncio
import json
import sys
from typing import Dict, Any

async def test_server():
    """Test the MCP server by sending JSON-RPC messages"""
    # Create a subprocess for the server
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Helper function to send a message
    async def send_message(message: Dict[str, Any]) -> Dict[str, Any]:
        message_str = json.dumps(message) + "\n"
        proc.stdin.write(message_str.encode())
        await proc.stdin.drain()
        
        # Read response
        response_line = await proc.stdout.readline()
        return json.loads(response_line.decode())
    
    try:
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        init_response = await send_message(init_request)
        print("Initialize response:", json.dumps(init_response, indent=2))
        
        # List tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\nSending tools/list request...")
        tools_response = await send_message(list_tools_request)
        print("Tools response:", json.dumps(tools_response, indent=2))
        
        # Test rolling dice
        roll_dice_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "roll_dice",
                "arguments": {
                    "notation": "2d6+3"
                }
            }
        }
        
        print("\nSending roll_dice request...")
        roll_response = await send_message(roll_dice_request)
        print("Roll response:", json.dumps(roll_response, indent=2))
        
        # Test flipping a coin
        flip_coin_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "flip_coin",
                "arguments": {}
            }
        }
        
        print("\nSending flip_coin request...")
        flip_response = await send_message(flip_coin_request)
        print("Flip response:", json.dumps(flip_response, indent=2))
        
    finally:
        # Clean up
        proc.stdin.close()
        await proc.wait()

if __name__ == "__main__":
    asyncio.run(test_server())
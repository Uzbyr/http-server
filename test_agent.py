#!/usr/bin/env python3

import subprocess
import json
import sys
import time

def test_agent_creation():
    """Test the simplified agent creation functionality"""
    print("🤖 Testing Mistral Agent Creation")
    print("=" * 40)
    
    # Test cases
    tests = [
        {
            "name": "List Tools",
            "request": {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
        },
        {
            "name": "Create Mistral Agent",
            "request": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "create_mistral_agent",
                    "arguments": {
                        "name": "Test Assistant",
                        "description": "A helpful test assistant",
                        "instructions": "You are a helpful assistant that can answer questions and provide information.",
                        "model": "mistral-medium-2505",
                        "temperature": 0.7
                    }
                }
            }
        },
        {
            "name": "List Agents",
            "request": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "list_mistral_agents",
                    "arguments": {}
                }
            }
        }
    ]
    
    # Start the MCP server process
    print("🚀 Starting MCP Server...")
    process = subprocess.Popen(
        [sys.executable, "src/simple_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give server time to start
    time.sleep(2)
    
    try:
        for test in tests:
            print(f"\n🧪 Running test: {test['name']}")
            
            # Send request
            request_json = json.dumps(test["request"]) + "\n"
            process.stdin.write(request_json)
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📤 Response: {json.dumps(response, indent=2)}")
                
                # Check for errors
                if "error" in response:
                    print(f"❌ Error in {test['name']}: {response['error']}")
                else:
                    print(f"✅ {test['name']} passed!")
            else:
                print(f"❌ No response received for {test['name']}")
            
            time.sleep(1)  # Wait between tests
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("\n🏁 MCP server stopped")

if __name__ == "__main__":
    test_agent_creation()

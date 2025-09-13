#!/usr/bin/env python3

import json
import sys
import os
from typing import Dict, Any, List
from mistral_service import MistralAgentService

class SimpleMCPServer:
    def __init__(self):
        self.mistral_service = MistralAgentService()
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available MCP tools"""
        return [
            {
                "name": "create_mistral_agent",
                "description": "Create a new Mistral agent with specified configuration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the agent"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the agent"
                        },
                        "instructions": {
                            "type": "string",
                            "description": "System instructions for the agent"
                        },
                        "model": {
                            "type": "string",
                            "description": "Model to use for the agent (default: mistral-medium-2505)",
                            "default": "mistral-medium-2505"
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Temperature for the agent (0.0-2.0)",
                            "default": 0.7
                        }
                    },
                    "required": ["name", "description", "instructions"]
                }
            },
            {
                "name": "list_mistral_agents",
                "description": "List all available Mistral agents",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_agent_details",
                "description": "Get details of a specific Mistral agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the agent to get details for"
                        }
                    },
                    "required": ["agent_id"]
                }
            },
            {
                "name": "delete_mistral_agent",
                "description": "Delete a Mistral agent",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "ID of the agent to delete"
                        }
                    },
                    "required": ["agent_id"]
                }
            }
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming JSON-RPC requests"""
        try:
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})
            
            if method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "create_mistral_agent":
                    result = self.mistral_service.create_agent(
                        name=arguments["name"],
                        description=arguments["description"],
                        instructions=arguments["instructions"],
                        model=arguments.get("model", "mistral-medium-2505"),
                        temperature=arguments.get("temperature", 0.7)
                    )
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                
                elif tool_name == "list_mistral_agents":
                    result = self.mistral_service.list_agents()
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                
                elif tool_name == "get_agent_details":
                    result = self.mistral_service.get_agent_details(arguments["agent_id"])
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                
                elif tool_name == "delete_mistral_agent":
                    result = self.mistral_service.delete_agent(arguments["agent_id"])
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": result
                    }
                
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def run(self):
        """Run the MCP server on stdio"""
        print("LeChat Mistral Agent MCP Server (Python) running on stdio", file=sys.stderr)
        
        while True:
            try:
                line = input()
                if not line:
                    continue
                
                request = json.loads(line)
                response = self.handle_request(request)
                print(json.dumps(response))
                sys.stdout.flush()
            
            except EOFError:
                break
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

def main():
    """Main entry point"""
    server = SimpleMCPServer()
    server.run()

if __name__ == "__main__":
    main()
import os
from typing import Dict, List, Any, Optional
from mistralai import Mistral
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MistralAgentService:
    def __init__(self):
        self.api_key = os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is required")
        
        self.client = Mistral(api_key=self.api_key)
    
    def create_agent(self, name: str, description: str, instructions: str, 
                    model: str = "mistral-medium-2505", temperature: float = 0.7) -> Dict[str, Any]:
        """Create a new Mistral agent using the Python SDK"""
        try:
            agent = self.client.beta.agents.create(
                model=model,
                description=description,
                name=name,
                instructions=instructions,
                completion_args={
                    "temperature": temperature
                }
            )
            
            # Handle completion_args properly
            temp_value = 'N/A'
            if hasattr(agent, 'completion_args') and agent.completion_args:
                if hasattr(agent.completion_args, 'temperature'):
                    temp_value = agent.completion_args.temperature
                elif isinstance(agent.completion_args, dict):
                    temp_value = agent.completion_args.get('temperature', 'N/A')
            
            # Handle created_at properly
            created_str = 'N/A'
            if hasattr(agent, 'created_at') and agent.created_at:
                if hasattr(agent.created_at, 'strftime'):
                    created_str = agent.created_at.strftime('%m/%d/%Y, %I:%M:%S %p')
                else:
                    created_str = str(agent.created_at)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ Successfully created Mistral agent \"{agent.name}\" with ID: {agent.id}\n\n"
                               f"Description: {agent.description}\n"
                               f"Model: {agent.model}\n"
                               f"Temperature: {temp_value}\n"
                               f"Created: {created_str}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: Failed to create agent: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def list_agents(self) -> Dict[str, Any]:
        """List all available Mistral agents"""
        try:
            agents = self.client.beta.agents.list()
            agents_list = agents.data if hasattr(agents, 'data') else []
            
            if not agents_list:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No agents found. Create your first agent using the create_mistral_agent tool!"
                        }
                    ]
                }
            
            agent_list_text = "\n".join([
                f"• {agent.name} (ID: {agent.id})\n"
                f"  Description: {agent.description}\n"
                f"  Model: {agent.model}\n"
                f"  Created: {agent.created_at.strftime('%m/%d/%Y, %I:%M:%S %p') if hasattr(agent, 'created_at') else 'N/A'}\n"
                for agent in agents_list
            ])
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🤖 Available Mistral Agents ({len(agents_list)}):\n\n{agent_list_text}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: Failed to list agents: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def get_agent_details(self, agent_id: str) -> Dict[str, Any]:
        """Get details of a specific Mistral agent"""
        try:
            agent = self.client.beta.agents.retrieve(agent_id)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"🤖 Agent Details: {agent.name}\n\n"
                               f"ID: {agent.id}\n"
                               f"Description: {agent.description}\n"
                               f"Instructions: {agent.instructions}\n"
                               f"Model: {agent.model}\n"
                               f"Temperature: {getattr(agent, 'completion_args', {}).get('temperature', 'N/A')}\n"
                               f"Created: {agent.created_at.strftime('%m/%d/%Y, %I:%M:%S %p') if hasattr(agent, 'created_at') else 'N/A'}\n"
                               f"Updated: {agent.updated_at.strftime('%m/%d/%Y, %I:%M:%S %p') if hasattr(agent, 'updated_at') else 'N/A'}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: Failed to get agent details: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete a Mistral agent"""
        try:
            self.client.beta.agents.delete(agent_id)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ Successfully deleted agent with ID: {agent_id}"
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: Failed to delete agent: {str(e)}"
                    }
                ],
                "isError": True
            }

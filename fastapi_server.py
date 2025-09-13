#!/usr/bin/env python3

import os
import sys
import asyncio
import json
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
from dotenv import load_dotenv
from datetime import datetime
import threading
import time

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Mistral Agent Manager",
    description="API pour gérer les agents Mistral - Create, List, Delete + Game Actions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mistral API configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")

# Global state for game characters and their actions
game_state = {
    "characters": {},
    "last_update": None
}

# Lock for thread-safe access to game state
state_lock = threading.Lock()

# Background task control
cron_task = None
cron_running = False

# Pydantic models based on Mistral API documentation
class CompletionArgs(BaseModel):
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(default=None, gt=0)
    random_seed: Optional[int] = Field(default=None)

class FunctionTool(BaseModel):
    type: str = Field(default="function")
    function: Dict[str, Any]

class WebSearchTool(BaseModel):
    type: str = Field(default="web_search")

class CodeInterpreterTool(BaseModel):
    type: str = Field(default="code_interpreter")

class AgentCreationRequest(BaseModel):
    name: str = Field(..., description="Name of the agent")
    description: Optional[str] = Field(None, description="Description of the agent")
    instructions: Optional[str] = Field(None, description="Instruction prompt the model will follow")
    model: str = Field(..., description="Model to use")
    tools: Optional[List[Dict[str, Any]]] = Field(default=[], description="List of tools available to the agent")
    completion_args: Optional[CompletionArgs] = Field(default=None, description="Completion arguments")
    handoffs: Optional[List[str]] = Field(default=None, description="List of agent IDs for handoffs")

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    instructions: Optional[str]
    model: str
    tools: List[Dict[str, Any]]
    completion_args: Optional[Dict[str, Any]]
    handoffs: Optional[List[str]]
    created_at: str
    updated_at: str

class AgentListResponse(BaseModel):
    data: List[AgentResponse]
    has_more: bool
    first_id: Optional[str]
    last_id: Optional[str]

class ErrorResponse(BaseModel):
    error: str
    message: str

# Game action models
class GameAction(BaseModel):
    type: str = Field(..., description="Type of action (move, say, emote, etc.)")
    target: Optional[str] = Field(None, description="Target of the action")
    content: Optional[str] = Field(None, description="Content of the action")

class Character(BaseModel):
    name: str
    actions: List[GameAction] = []

class GameStateResponse(BaseModel):
    characters: Dict[str, Character]

# HTTP client for Mistral API
async def get_mistral_client():
    return httpx.AsyncClient(
        base_url=MISTRAL_BASE_URL,
        headers={
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        },
        timeout=30.0
    )

# Function to get agent actions from Mistral
async def get_agent_action(agent_id: str, agent_name: str) -> Optional[GameAction]:
    """Get a single action from an agent"""
    try:
        async with await get_mistral_client() as client:
            # Create a completion request to get an action
            completion_data = {
                "model": "mistral-medium-2505",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""You are {agent_name}, a character in a virtual world game. 
                        Generate a single action in JSON format. The action must be one of these types:
                        - "move": Move to a location (target: direction, content: description)
                        - "say": Say something (target: who to speak to, content: what to say)
                        - "emote": Perform an emotion/gesture (target: who to emote to, content: what emotion/gesture)
                        
                        Return ONLY a JSON object with this exact format:
                        {{
                            "type": "move|say|emote",
                            "target": "optional_target",
                            "content": "action_description"
                        }}
                        
                        Be creative and make the action interesting for a game!"""
                    },
                    {
                        "role": "user",
                        "content": f"Generate your next action as {agent_name} in the game world."
                    }
                ],
                "max_tokens": 150,
                "temperature": 0.8
            }
            
            response = await client.post("/chat/completions", json=completion_data)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"].strip()
                
                # Try to parse JSON from the response
                try:
                    # Extract JSON from the response (in case there's extra text)
                    start = content.find('{')
                    end = content.rfind('}') + 1
                    if start != -1 and end != 0:
                        json_str = content[start:end]
                        action_data = json.loads(json_str)
                        
                        return GameAction(
                            type=action_data.get("type", "emote"),
                            target=action_data.get("target"),
                            content=action_data.get("content", f"{agent_name} did something")
                        )
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing action for {agent_name}: {e}")
                    # Fallback action
                    return GameAction(
                        type="emote",
                        target="self",
                        content=f"{agent_name} is thinking..."
                    )
            else:
                print(f"Error getting action for {agent_name}: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"Exception getting action for {agent_name}: {e}")
        return None

# Function to update game state with agent actions
async def update_game_state():
    """Update game state by fetching actions from all agents"""
    global game_state, cron_running
    
    if not cron_running:
        return
        
    try:
        # Get all agents
        async with await get_mistral_client() as client:
            response = await client.get("/agents")
            
            if response.status_code == 200:
                data = response.json()
                agents = data if isinstance(data, list) else data.get("data", [])
                
                # Process agents in parallel
                tasks = []
                for agent in agents:
                    agent_id = agent.get("id")
                    agent_name = agent.get("name", f"Agent-{agent_id}")
                    
                    # Create character if doesn't exist
                    char_id = f"char-{agent_id[-8:]}"  # Use last 8 chars of agent ID
                    
                    with state_lock:
                        if char_id not in game_state["characters"]:
                            game_state["characters"][char_id] = {
                                "name": agent_name,
                                "actions": []
                            }
                    
                    # Get action for this agent
                    task = get_agent_action(agent_id, agent_name)
                    tasks.append((char_id, task))
                
                # Wait for all actions to complete
                for char_id, task in tasks:
                    action = await task
                    if action:
                        with state_lock:
                            if char_id in game_state["characters"]:
                                # Add new action to the beginning of the list
                                game_state["characters"][char_id]["actions"].insert(0, action.dict())
                                
                                # Keep only last 10 actions per character
                                if len(game_state["characters"][char_id]["actions"]) > 10:
                                    game_state["characters"][char_id]["actions"] = game_state["characters"][char_id]["actions"][:10]
                
                # Update last update time
                with state_lock:
                    game_state["last_update"] = datetime.now().isoformat()
                    
                print(f"Updated game state with {len(agents)} agents at {game_state['last_update']}")
                
    except Exception as e:
        print(f"Error updating game state: {e}")

# Background cron job
async def cron_job():
    """Background task that runs every 5 seconds"""
    global cron_running
    
    while cron_running:
        try:
            await update_game_state()
            await asyncio.sleep(5)  # Wait 5 seconds
        except Exception as e:
            print(f"Error in cron job: {e}")
            await asyncio.sleep(5)

# Start/Stop cron job functions
def start_cron_job():
    """Start the background cron job"""
    global cron_task, cron_running
    
    if not cron_running:
        cron_running = True
        cron_task = asyncio.create_task(cron_job())
        print("Cron job started")

def stop_cron_job():
    """Stop the background cron job"""
    global cron_task, cron_running
    
    if cron_running:
        cron_running = False
        if cron_task:
            cron_task.cancel()
        print("Cron job stopped")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Mistral Agent Manager API + Game Engine",
        "version": "1.0.0",
        "endpoints": {
            "create_agent": "POST /agents",
            "list_agents": "GET /agents",
            "get_agent_by_id": "GET /agents/{agent_id}",
            "get_agent_by_name": "GET /agents/search/{agent_name}",
            "delete_agent": "DELETE /agents/{agent_id}",
            "game_state": "GET /game/state",
            "start_game": "POST /game/start",
            "stop_game": "POST /game/stop"
        }
    }

@app.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_request: AgentCreationRequest):
    """
    Créer un nouvel agent Mistral
    
    - **name**: Nom de l'agent (requis)
    - **description**: Description de l'agent (optionnel)
    - **instructions**: Instructions système pour l'agent (optionnel)
    - **model**: Modèle à utiliser (requis)
    - **tools**: Liste des outils disponibles (optionnel)
    - **completion_args**: Arguments de complétion (optionnel)
    - **handoffs**: Liste des IDs d'agents pour les transferts (optionnel)
    """
    try:
        async with await get_mistral_client() as client:
            # Prepare the request body according to Mistral API
            request_body = {
                "name": agent_request.name,
                "model": agent_request.model
            }
            
            if agent_request.description:
                request_body["description"] = agent_request.description
            if agent_request.instructions:
                request_body["instructions"] = agent_request.instructions
            if agent_request.tools:
                request_body["tools"] = agent_request.tools
            if agent_request.completion_args:
                request_body["completion_args"] = agent_request.completion_args.dict(exclude_none=True)
            if agent_request.handoffs:
                request_body["handoffs"] = agent_request.handoffs
            
            response = await client.post("/agents", json=request_body)
            
            if response.status_code == 200:
                agent_data = response.json()
                return AgentResponse(**agent_data)
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erreur lors de la création de l'agent: {error_detail}"
                )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur de connexion à l'API Mistral: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )

@app.get("/agents", response_model=AgentListResponse)
async def list_agents(page: Optional[int] = None):
    """
    Lister tous les agents Mistral
    
    - **page**: Numéro de page pour la pagination (optionnel)
    """
    try:
        async with await get_mistral_client() as client:
            params = {}
            if page is not None:
                params["page"] = page
            
            response = await client.get("/agents", params=params)
            
            if response.status_code == 200:
                data = response.json()
                # L'API Mistral retourne directement une liste d'agents
                if isinstance(data, list):
                    return AgentListResponse(
                        data=[AgentResponse(**agent) for agent in data],
                        has_more=False,
                        first_id=data[0]["id"] if data else None,
                        last_id=data[-1]["id"] if data else None
                    )
                else:
                    return AgentListResponse(**data)
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erreur lors de la récupération des agents: {error_detail}"
                )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur de connexion à l'API Mistral: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """
    Récupérer les détails d'un agent spécifique
    
    - **agent_id**: ID de l'agent à récupérer
    """
    try:
        async with await get_mistral_client() as client:
            response = await client.get(f"/agents/{agent_id}")
            
            if response.status_code == 200:
                agent_data = response.json()
                return AgentResponse(**agent_data)
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent avec l'ID '{agent_id}' non trouvé"
                )
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erreur lors de la récupération de l'agent: {error_detail}"
                )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur de connexion à l'API Mistral: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )

@app.delete("/agents/{agent_id}", response_model=Dict[str, str])
async def delete_agent(agent_id: str):
    """
    Supprimer un agent Mistral
    
    - **agent_id**: ID de l'agent à supprimer
    """
    try:
        async with await get_mistral_client() as client:
            response = await client.delete(f"/agents/{agent_id}")
            
            if response.status_code in [200, 204]:
                return {"message": f"Agent '{agent_id}' supprimé avec succès"}
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Agent avec l'ID '{agent_id}' non trouvé"
                )
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erreur lors de la suppression de l'agent: {error_detail}"
                )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur de connexion à l'API Mistral: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )

@app.get("/agents/search/{agent_name}", response_model=Dict[str, str])
async def get_agent_id_by_name(agent_name: str):
    """
    Récupérer l'ID d'un agent à partir de son nom
    
    - **agent_name**: Nom de l'agent à rechercher
    """
    try:
        async with await get_mistral_client() as client:
            response = await client.get("/agents")
            
            if response.status_code == 200:
                data = response.json()
                # L'API Mistral retourne directement une liste d'agents
                if isinstance(data, list):
                    agents = data
                else:
                    agents = data.get("data", [])
                
                # Rechercher l'agent par nom (insensible à la casse)
                for agent in agents:
                    if agent.get("name", "").lower() == agent_name.lower():
                        return {
                            "agent_name": agent["name"],
                            "agent_id": agent["id"],
                            "description": agent.get("description", ""),
                            "model": agent.get("model", ""),
                            "created_at": agent.get("created_at", "")
                        }
                
                # Si aucun agent trouvé
                return {
                    "error": "Agent not found",
                    "message": f"Aucun agent trouvé avec le nom '{agent_name}'",
                    "agent_name": agent_name
                }
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Erreur lors de la recherche de l'agent: {error_detail}"
                )
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur de connexion à l'API Mistral: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur interne: {str(e)}"
        )

@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Vérification de l'état de l'API"""
    return {"status": "healthy", "message": "API Mistral Agent Manager + Game Engine opérationnelle"}

# Game endpoints
@app.get("/game/state", response_model=GameStateResponse)
async def get_game_state():
    """Get the current game state with all characters and their actions"""
    with state_lock:
        return GameStateResponse(characters=game_state["characters"])

@app.post("/game/start")
async def start_game():
    """Start the game cron job that fetches agent actions every 5 seconds"""
    start_cron_job()
    return {"message": "Game started! Agents will now generate actions every 5 seconds."}

@app.post("/game/stop")
async def stop_game():
    """Stop the game cron job"""
    stop_cron_job()
    return {"message": "Game stopped! No more actions will be generated."}

@app.get("/game/status")
async def get_game_status():
    """Get the current game status"""
    with state_lock:
        return {
            "running": cron_running,
            "characters_count": len(game_state["characters"]),
            "last_update": game_state["last_update"]
        }

# Startup event to start the cron job automatically
@app.on_event("startup")
async def startup_event():
    """Start the cron job when the server starts"""
    start_cron_job()

# Shutdown event to stop the cron job
@app.on_event("shutdown")
async def shutdown_event():
    """Stop the cron job when the server shuts down"""
    stop_cron_job()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

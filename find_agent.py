#!/usr/bin/env python3

import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

async def find_agent(agent_name: str):
    """Trouver un agent par son nom et afficher ses informations"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/agents/search/{agent_name}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Vérifier si c'est une erreur (agent non trouvé)
                if "error" in result:
                    print(f"❌ {result['message']}")
                    return None
                
                # Afficher les informations de l'agent
                print(f"✅ Agent trouvé: {result['agent_name']}")
                print(f"🆔 ID: {result['agent_id']}")
                print(f"📄 Description: {result['description']}")
                print(f"🧠 Modèle: {result['model']}")
                print(f"📅 Créé le: {result['created_at']}")
                
                return result['agent_id']
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                return None
                
        except httpx.ConnectError:
            print("❌ Erreur: Impossible de se connecter au serveur FastAPI")
            print("💡 Assurez-vous que le serveur est démarré avec: python start_server.py")
            return None
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return None

async def list_agents():
    """Lister tous les agents disponibles"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/agents")
            
            if response.status_code == 200:
                agents = response.json()
                agent_list = agents.get('data', [])
                
                print(f"📊 Nombre d'agents: {len(agent_list)}")
                print("🎯 Agents disponibles:")
                for i, agent in enumerate(agent_list, 1):
                    print(f"   {i}. {agent['name']}")
                
                return agent_list
            else:
                print(f"❌ Erreur HTTP {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return []

def main():
    """Fonction principale"""
    if len(sys.argv) < 2:
        print("🔍 Recherche d'agents par nom")
        print("=" * 40)
        print("Usage:")
        print("  python find_agent.py <nom_agent>     # Trouver un agent spécifique")
        print("  python find_agent.py --list          # Lister tous les agents")
        print("  python find_agent.py --help          # Afficher cette aide")
        print()
        print("Exemples:")
        print("  python find_agent.py 'Example Code Assistant'")
        print("  python find_agent.py 'test agent'")
        print("  python find_agent.py --list")
        return
    
    command = sys.argv[1]
    
    if command == "--help" or command == "-h":
        print("🔍 Recherche d'agents par nom")
        print("=" * 40)
        print("Ce script permet de trouver un agent Mistral par son nom.")
        print()
        print("Commandes disponibles:")
        print("  <nom_agent>     Rechercher un agent par nom")
        print("  --list, -l      Lister tous les agents disponibles")
        print("  --help, -h      Afficher cette aide")
        print()
        print("La recherche est insensible à la casse.")
        return
    
    if command == "--list" or command == "-l":
        asyncio.run(list_agents())
        return
    
    # Rechercher l'agent
    agent_name = command
    agent_id = asyncio.run(find_agent(agent_name))
    
    if agent_id:
        print(f"\n💡 Vous pouvez maintenant utiliser l'ID '{agent_id}' pour d'autres opérations.")
        print(f"   Exemple: curl -X DELETE 'http://localhost:8000/agents/{agent_id}'")

if __name__ == "__main__":
    main()

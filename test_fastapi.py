#!/usr/bin/env python3

import asyncio
import httpx
import json
import sys

BASE_URL = "http://localhost:8000"

async def test_fastapi_server():
    """Test du serveur FastAPI Mistral Agent Manager"""
    print("🚀 Test du serveur FastAPI Mistral Agent Manager")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: Health check
            print("\n1. Test Health Check")
            response = await client.get(f"{BASE_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test 2: Root endpoint
            print("\n2. Test Root Endpoint")
            response = await client.get(f"{BASE_URL}/")
            print(f"Status: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            # Test 3: List agents (before creating)
            print("\n3. Test List Agents (avant création)")
            response = await client.get(f"{BASE_URL}/agents")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                agents = response.json()
                print(f"Nombre d'agents: {len(agents.get('data', []))}")
            else:
                print(f"Erreur: {response.text}")
            
            # Test 4: Create agent
            print("\n4. Test Create Agent")
            agent_data = {
                "name": "Assistant Test",
                "description": "Un assistant de test créé via FastAPI",
                "instructions": "Tu es un assistant utile qui peut répondre aux questions et fournir des informations.",
                "model": "mistral-medium-2505",
                "completion_args": {
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            }
            
            response = await client.post(f"{BASE_URL}/agents", json=agent_data)
            print(f"Status: {response.status_code}")
            if response.status_code == 201:
                created_agent = response.json()
                agent_id = created_agent["id"]
                print(f"✅ Agent créé avec succès!")
                print(f"ID: {agent_id}")
                print(f"Nom: {created_agent['name']}")
                print(f"Modèle: {created_agent['model']}")
            else:
                print(f"❌ Erreur lors de la création: {response.text}")
                return
            
            # Test 5: Get specific agent
            print(f"\n5. Test Get Agent {agent_id}")
            response = await client.get(f"{BASE_URL}/agents/{agent_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                agent = response.json()
                print(f"✅ Agent récupéré: {agent['name']}")
            else:
                print(f"❌ Erreur: {response.text}")
            
            # Test 6: List agents (after creating)
            print("\n6. Test List Agents (après création)")
            response = await client.get(f"{BASE_URL}/agents")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                agents = response.json()
                print(f"Nombre d'agents: {len(agents.get('data', []))}")
                for agent in agents.get('data', []):
                    print(f"  - {agent['name']} (ID: {agent['id']})")
            else:
                print(f"Erreur: {response.text}")
            
            # Test 7: Delete agent
            print(f"\n7. Test Delete Agent {agent_id}")
            response = await client.delete(f"{BASE_URL}/agents/{agent_id}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"✅ Agent supprimé avec succès!")
            else:
                print(f"❌ Erreur lors de la suppression: {response.text}")
            
            # Test 8: List agents (after deletion)
            print("\n8. Test List Agents (après suppression)")
            response = await client.get(f"{BASE_URL}/agents")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                agents = response.json()
                print(f"Nombre d'agents: {len(agents.get('data', []))}")
            else:
                print(f"Erreur: {response.text}")
            
            print("\n🎉 Tous les tests terminés!")
            
        except httpx.ConnectError:
            print("❌ Erreur: Impossible de se connecter au serveur FastAPI")
            print("Assurez-vous que le serveur est démarré avec: python fastapi_server.py")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    asyncio.run(test_fastapi_server())

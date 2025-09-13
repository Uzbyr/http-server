#!/usr/bin/env python3

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_search_endpoint():
    """Test du nouvel endpoint de recherche d'agents par nom"""
    print("🔍 Test de l'endpoint de recherche d'agents par nom")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Lister tous les agents pour voir les noms disponibles
            print("\n1. 📋 Liste des agents disponibles")
            response = await client.get(f"{BASE_URL}/agents")
            if response.status_code == 200:
                agents = response.json()
                agent_list = agents.get('data', [])
                print(f"   📊 Nombre d'agents: {len(agent_list)}")
                print("   🎯 Noms d'agents disponibles:")
                for i, agent in enumerate(agent_list[:5]):
                    print(f"      {i+1}. {agent['name']}")
            else:
                print(f"   ❌ Erreur: {response.text}")
                return
            
            # 2. Tester la recherche avec un nom existant
            print("\n2. 🔍 Recherche d'un agent existant")
            test_name = agent_list[0]['name'] if agent_list else "Test Agent"
            response = await client.get(f"{BASE_URL}/agents/search/{test_name}")
            print(f"   Recherche de: '{test_name}'")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Agent trouvé!")
                print(f"   📝 Nom: {result['agent_name']}")
                print(f"   🆔 ID: {result['agent_id']}")
                print(f"   📄 Description: {result['description']}")
                print(f"   🧠 Modèle: {result['model']}")
                print(f"   📅 Créé le: {result['created_at']}")
            else:
                print(f"   ❌ Erreur: {response.text}")
            
            # 3. Tester la recherche avec un nom inexistant
            print("\n3. 🔍 Recherche d'un agent inexistant")
            fake_name = "AgentInexistant123"
            response = await client.get(f"{BASE_URL}/agents/search/{fake_name}")
            print(f"   Recherche de: '{fake_name}'")
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 404:
                error = response.json()
                print(f"   ✅ Erreur 404 attendue: {error['detail']}")
            else:
                print(f"   ❌ Status inattendu: {response.status_code}")
                print(f"   Response: {response.text}")
            
            # 4. Tester la recherche insensible à la casse
            print("\n4. 🔍 Test de recherche insensible à la casse")
            if agent_list:
                original_name = agent_list[0]['name']
                # Tester avec différentes casses
                test_cases = [
                    original_name.upper(),
                    original_name.lower(),
                    original_name.capitalize()
                ]
                
                for test_case in test_cases:
                    response = await client.get(f"{BASE_URL}/agents/search/{test_case}")
                    print(f"   Recherche de: '{test_case}' -> Status: {response.status_code}")
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Trouvé: {result['agent_name']} (ID: {result['agent_id'][:20]}...)")
                    else:
                        print(f"   ❌ Non trouvé")
            
            print("\n🎉 Tests de recherche terminés!")
            
        except httpx.ConnectError:
            print("❌ Erreur: Impossible de se connecter au serveur FastAPI")
            print("💡 Assurez-vous que le serveur est démarré avec: python start_server.py")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    asyncio.run(test_search_endpoint())

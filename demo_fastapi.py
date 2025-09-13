#!/usr/bin/env python3

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def demo_fastapi():
    """Démonstration du serveur FastAPI Mistral Agent Manager"""
    print("🎯 Démonstration du serveur FastAPI Mistral Agent Manager")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        try:
            # 1. Vérifier l'état de l'API
            print("\n1. 📊 État de l'API")
            response = await client.get(f"{BASE_URL}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Message: {response.json()['message']}")
            
            # 2. Créer un agent de démonstration
            print("\n2. 🤖 Création d'un agent de démonstration")
            agent_data = {
                "name": "Assistant Démo",
                "description": "Un assistant créé pour la démonstration",
                "instructions": "Tu es un assistant de démonstration très utile qui peut répondre aux questions et fournir des informations détaillées.",
                "model": "mistral-medium-2505",
                "completion_args": {
                    "temperature": 0.8,
                    "max_tokens": 1500
                }
            }
            
            response = await client.post(f"{BASE_URL}/agents", json=agent_data)
            if response.status_code == 201:
                agent = response.json()
                agent_id = agent["id"]
                print(f"   ✅ Agent créé avec succès!")
                print(f"   📝 Nom: {agent['name']}")
                print(f"   🆔 ID: {agent_id}")
                print(f"   🧠 Modèle: {agent['model']}")
                print(f"   🌡️ Température: {agent['completion_args']['temperature']}")
            else:
                print(f"   ❌ Erreur: {response.text}")
                return
            
            # 3. Lister tous les agents
            print("\n3. 📋 Liste des agents")
            response = await client.get(f"{BASE_URL}/agents")
            if response.status_code == 200:
                agents = response.json()
                print(f"   📊 Nombre total d'agents: {len(agents['data'])}")
                print("   🎯 Derniers agents créés:")
                for i, agent in enumerate(agents['data'][:5]):  # Afficher les 5 premiers
                    print(f"      {i+1}. {agent['name']} (ID: {agent['id'][:20]}...)")
            else:
                print(f"   ❌ Erreur: {response.text}")
            
            # 4. Récupérer les détails de l'agent créé
            print(f"\n4. 🔍 Détails de l'agent '{agent_id[:20]}...'")
            response = await client.get(f"{BASE_URL}/agents/{agent_id}")
            if response.status_code == 200:
                agent = response.json()
                print(f"   📝 Nom: {agent['name']}")
                print(f"   📄 Description: {agent['description']}")
                print(f"   📋 Instructions: {agent['instructions'][:100]}...")
                print(f"   🧠 Modèle: {agent['model']}")
                print(f"   📅 Créé le: {agent['created_at']}")
            else:
                print(f"   ❌ Erreur: {response.text}")
            
            # 5. Supprimer l'agent de démonstration
            print(f"\n5. 🗑️ Suppression de l'agent de démonstration")
            response = await client.delete(f"{BASE_URL}/agents/{agent_id}")
            if response.status_code == 200:
                print(f"   ✅ Agent supprimé avec succès!")
                print(f"   📝 Message: {response.json()['message']}")
            else:
                print(f"   ❌ Erreur: {response.text}")
            
            # 6. Vérification finale
            print("\n6. ✅ Vérification finale")
            response = await client.get(f"{BASE_URL}/agents")
            if response.status_code == 200:
                agents = response.json()
                print(f"   📊 Nombre d'agents après suppression: {len(agents['data'])}")
            
            print("\n🎉 Démonstration terminée avec succès!")
            print("🌐 Vous pouvez maintenant utiliser l'API à l'adresse: http://localhost:8000")
            print("📚 Documentation disponible sur: http://localhost:8000/docs")
            
        except httpx.ConnectError:
            print("❌ Erreur: Impossible de se connecter au serveur FastAPI")
            print("💡 Assurez-vous que le serveur est démarré avec: python start_server.py")
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    asyncio.run(demo_fastapi())

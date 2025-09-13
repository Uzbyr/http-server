# 🌐 HTTP Server (FastAPI) - Mistral Agent Manager

Ce dossier contient le serveur HTTP FastAPI pour la gestion des agents Mistral.

## 📁 Structure

```
http-server/
├── fastapi_server.py      # Serveur FastAPI principal
├── test_fastapi.py        # Tests du serveur FastAPI
├── demo_fastapi.py        # Script de démonstration
├── test_search_endpoint.py # Tests de l'endpoint de recherche
├── find_agent.py          # Script pour rechercher des agents
├── create_agent.py        # Script pour créer des agents
├── test_agent.py          # Tests des agents
├── start_server.py        # Script de démarrage du serveur
├── start_demo.sh          # Script bash de démonstration
├── requirements.txt       # Dépendances Python
├── setup_python.sh        # Script d'installation
├── src/                   # Services et utilitaires
│   └── mistral_service.py # Service d'intégration Mistral
└── venv/                  # Environnement virtuel Python
```

## 🚀 Démarrage rapide

1. **Installer les dépendances :**
   ```bash
   cd http-server
   chmod +x setup_python.sh
   ./setup_python.sh
   ```

2. **Démarrer le serveur :**
   ```bash
   source venv/bin/activate
   python start_server.py
   ```

3. **Tester le serveur :**
   ```bash
   python test_fastapi.py
   ```

## 🔗 Endpoints disponibles

- `GET /` - Page d'accueil
- `POST /agents` - Créer un agent
- `GET /agents` - Lister tous les agents
- `GET /agents/{agent_id}` - Détails d'un agent
- `DELETE /agents/{agent_id}` - Supprimer un agent
- `GET /agents/search/{agent_name}` - Rechercher un agent par nom
- `GET /health` - Vérification de santé

## 📖 Documentation

Une fois le serveur démarré, accédez à :
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🛠️ Scripts utiles

- `python create_agent.py` - Créer un agent interactivement
- `python find_agent.py "Nom Agent"` - Rechercher un agent
- `python find_agent.py --list` - Lister tous les agents
- `python demo_fastapi.py` - Démonstration complète

#!/bin/bash

echo "🚀 Démarrage du serveur FastAPI Mistral Agent Manager"
echo "======================================================"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Exécutez d'abord: ./setup_python.sh"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si la clé API est définie
if [ -z "$MISTRAL_API_KEY" ]; then
    echo "❌ MISTRAL_API_KEY non définie. Vérifiez votre fichier .env"
    exit 1
fi

echo "✅ Environnement configuré"
echo "🌐 Démarrage du serveur sur http://localhost:8000"
echo "📚 Documentation: http://localhost:8000/docs"
echo "🔧 Redoc: http://localhost:8000/redoc"
echo ""
echo "💡 Pour tester l'API, ouvrez un autre terminal et exécutez:"
echo "   python demo_fastapi.py"
echo ""
echo "🛑 Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Démarrer le serveur
python start_server.py

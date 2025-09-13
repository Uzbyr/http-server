#!/usr/bin/env python3

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("🚀 Démarrage du serveur FastAPI Mistral Agent Manager")
    print("=" * 60)
    print("📡 API disponible sur: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("🔧 Redoc: http://localhost:8000/redoc")
    print("=" * 60)
    
    # Check if MISTRAL_API_KEY is set
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ ERREUR: MISTRAL_API_KEY n'est pas défini!")
        print("Veuillez définir votre clé API Mistral dans le fichier .env")
        exit(1)
    
    print("✅ Clé API Mistral trouvée")
    print("🔄 Démarrage du serveur...")
    
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    origins = [
        "http://localhost:3000",  # frontend local
        "https://projet-ia-osi4.vercel.app/",  # frontend en ligne sur vercel
        # ajoute ici les autres origines si besoin (ex : déploiement)
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,           # Liste des domaines autorisés
        allow_credentials=True,
        allow_methods=["*"],             # GET, POST, etc.
        allow_headers=["*"],             # Autorise tous les headers
    )
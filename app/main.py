"""Point d'entrée de l'API. Lancement : uvicorn app.main:app --reload (depuis la racine du projet)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import VERSION
from .documentation import DESCRIPTION, TAGS
from .ressources import charger_ressources, liberer_ressources
from .routes import monitoring, prevision, supervision
from .validation import EntreeInvalide


@asynccontextmanager
async def lifespan(app: FastAPI):
    charger_ressources()    # au démarrage : modèle et tables de référence
    yield
    liberer_ressources()    # à l'arrêt


app = FastAPI(title="Prédiction de ventes (Favorita)", version=VERSION,
              description=DESCRIPTION, openapi_tags=TAGS, lifespan=lifespan)

app.include_router(prevision.router)
app.include_router(supervision.router)
app.include_router(monitoring.router)


@app.exception_handler(EntreeInvalide)
async def gerer_entree_invalide(requete: Request, erreur: EntreeInvalide):
    """Une règle métier est violée : on répond 422 avec le message explicatif."""
    return JSONResponse(status_code=422, content={"detail": str(erreur)})

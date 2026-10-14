"""Route de prévision : POST /predict."""
from fastapi import APIRouter

from ..documentation import DESCRIPTION_PREDICT, EXEMPLE_ERREUR_422
from ..prevision import predire
from ..schemas import Reponse, Requete

router = APIRouter(tags=["Prévision"])


@router.post(
    "/predict",
    response_model=Reponse,
    summary="Prédire les ventes des prochains jours",
    description=DESCRIPTION_PREDICT,
    response_description="Ventes prévues jour par jour, total, et avertissements éventuels.",
    responses={422: {
        "description": "Entrée refusée : le message `detail` explique la règle non respectée.",
        "content": {"application/json": {"example": EXEMPLE_ERREUR_422}},
    }})
def predict(requete: Requete):
    return predire(requete)

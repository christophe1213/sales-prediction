"""Routes de supervision : savoir si le service va bien et ce qu'il accepte."""
from fastapi import APIRouter

from ..config import HISTORIQUE_MIN, HORIZON, VERSION
from ..ressources import ETAT

router = APIRouter(tags=["Supervision"])


@router.get("/health", summary="État du service")
def health():
    """Indique que le service tourne, avec la version du modèle, la date de fin de son
    entraînement, son erreur de référence (RMSLE du backtest) et les limites d'utilisation."""
    meta = ETAT["meta_modele"]
    return {"statut": "ok",
            "modele_version": VERSION,
            "entraine_jusqu_au": meta["fin_entrainement"],
            "rmsle_backtest": meta["rmsle_backtest_5_fenetres"],
            "horizon_max_jours": HORIZON,
            "historique_min_jours": HISTORIQUE_MIN}


@router.get("/options", summary="Magasins et familles acceptés")
def options():
    """Valeurs que `POST /predict` accepte pour `store_nbr` et `family`.
    Toute autre valeur est refusée (erreur 422)."""
    return {"magasins": sorted(ETAT["ref"]["stores"].index.tolist()),
            "familles": ETAT["categories"]["family"]}

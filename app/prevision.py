"""Le cœur du service : transformer une requête valide en prévision."""
import numpy as np
import pandas as pd

from .preparation import construire_features

from .config import VERSION
from .ressources import ETAT
from .schemas import PrevisionJour, Reponse, Requete
from .validation import verifier_requete


def _avertissements(req: Requete, dates: pd.DatetimeIndex) -> list[str]:
    """Liste ce qui rend la prévision moins fiable, pour que le client le sache."""
    messages = []

    if req.promotions is None:
        messages.append("promotions non fournies : supposées nulles, "
                        "les ventes peuvent être sous-estimées")

    fin_feries = ETAT["fin_feries"]
    if dates[-1].date() > fin_feries:
        messages.append(f"jours fériés connus seulement jusqu'au {fin_feries} : "
                        "les jours fériés plus tardifs sont ignorés")

    if dates[-1].year > 2017:
        messages.append("le modèle a appris sur 2013-2017 (supermarché équatorien) : "
                        "prévision non validée pour cette période")

    if (dates.month == 12).any():
        messages.append("décembre : période où l'erreur du modèle est plus élevée")

    return messages


def predire(req: Requete) -> Reponse:
    dates, historique = verifier_requete(req, ETAT["ref"], ETAT["categories"])

    variables = construire_features(
        req.store_nbr, req.family, dates, historique, req.promotions,
        ETAT["ref"], ETAT["categories"], ETAT["meta_modele"]["features"])

    # Le modèle a été entraîné sur log(1 + ventes) : on revient aux unités avec expm1.
    ventes = np.expm1(ETAT["modele"].predict(variables)).clip(min=0).round(1)

    return Reponse(
        store_nbr=req.store_nbr,
        family=req.family,
        predictions=[PrevisionJour(date=jour.date(), sales=float(v))
                     for jour, v in zip(dates, ventes)],
        total=float(ventes.sum().round(1)),
        modele_version=VERSION,
        avertissements=_avertissements(req, dates))

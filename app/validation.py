"""Les règles que doit respecter une requête avant qu'on lance le modèle.

Ce fichier ne connaît pas FastAPI : il lève simplement `EntreeInvalide`, et c'est
main.py qui la transforme en erreur 422. Résultat, on peut tester ces règles
avec pytest sans démarrer le serveur.
"""
import pandas as pd

from .config import HISTORIQUE_MIN, HORIZON
from .schemas import Requete


class EntreeInvalide(ValueError):
    """Une règle n'est pas respectée. Le message est renvoyé tel quel au client."""


def _verifier_magasin_famille_promotions(req: Requete, ref, categories):
    if req.store_nbr not in ref["stores"].index:
        raise EntreeInvalide(f"magasin inconnu : {req.store_nbr} (voir /options)")
    if req.family not in categories["family"]:
        raise EntreeInvalide(f"famille inconnue : {req.family} (voir /options)")

    if req.promotions is None:
        return
    if len(req.promotions) != req.nb_jours:
        raise EntreeInvalide(
            f"promotions : {len(req.promotions)} valeurs reçues, {req.nb_jours} attendues")
    if min(req.promotions) < 0:
        raise EntreeInvalide("promotions : valeurs négatives interdites")


def _lire_historique(req: Requete) -> pd.Series:
    historique = pd.Series({pd.Timestamp(v.date): v.sales for v in req.historique},
                           dtype="float64")
    if len(historique) != len(req.historique):
        raise EntreeInvalide("historique : une date apparaît plusieurs fois")
    if historique.empty:
        raise EntreeInvalide("historique vide")
    return historique


def verifier_requete(req: Requete, ref, categories):
    """Contrôle toute la requête. Renvoie (dates à prédire, historique sous forme de Series)."""
    _verifier_magasin_famille_promotions(req, ref, categories)

    dates = pd.date_range(req.date_debut, periods=req.nb_jours, freq="D")
    historique = _lire_historique(req)
    premier_jour, dernier_jour = historique.index.min(), historique.index.max()

    if dernier_jour >= dates[0]:
        raise EntreeInvalide(
            f"historique : il doit se terminer avant date_debut ({req.date_debut}), "
            f"dernier jour reçu : {dernier_jour.date()}")

    limite_debut = dates[0] - pd.Timedelta(days=HISTORIQUE_MIN)
    if premier_jour > limite_debut:
        raise EntreeInvalide(
            f"historique trop court : il doit commencer au plus tard le {limite_debut.date()} "
            f"({HISTORIQUE_MIN} jours avant date_debut), premier jour reçu : {premier_jour.date()}")

    ecart = (dates[-1] - dernier_jour).days
    if ecart > HORIZON:
        raise EntreeInvalide(
            f"horizon trop lointain : le dernier jour prédit est à {ecart} jours du dernier "
            f"jour connu ({dernier_jour.date()}), maximum {HORIZON}")

    return dates, historique

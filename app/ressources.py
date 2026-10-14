"""Tout ce qu'il faut charger une seule fois au démarrage : le modèle et les tables de référence.

Charger le modèle à chaque requête serait très lent, alors on le garde en mémoire
dans le dictionnaire ETAT, que les routes consultent ensuite.
"""
import json

import joblib
import pandas as pd
import sklearn

from .preparation import preparer_references

from .config import (CHEMIN_FERIES, CHEMIN_MAGASINS, CHEMIN_META_DONNEES,
                     CHEMIN_META_MODELE, CHEMIN_MODELE)

ETAT: dict = {}


def _verifier_version_sklearn(meta_modele):
    """Un modèle sauvegardé avec une autre version de scikit-learn peut mal se comporter."""
    version_entrainement = meta_modele["sklearn"]
    if version_entrainement != sklearn.__version__:
        raise RuntimeError(
            f"Le modèle a été entraîné avec scikit-learn {version_entrainement}, "
            f"mais {sklearn.__version__} est installé. "
            f"Installe la bonne version : pip install scikit-learn=={version_entrainement}")


def charger_ressources():
    meta_modele = json.loads(CHEMIN_META_MODELE.read_text(encoding="utf-8"))
    _verifier_version_sklearn(meta_modele)

    magasins = pd.read_csv(CHEMIN_MAGASINS)
    feries = pd.read_csv(CHEMIN_FERIES)

    ETAT["modele"] = joblib.load(CHEMIN_MODELE)
    ETAT["meta_modele"] = meta_modele
    ETAT["categories"] = json.loads(CHEMIN_META_DONNEES.read_text(encoding="utf-8"))["categories"]
    ETAT["ref"] = preparer_references(magasins, feries)
    # Au-delà de cette date, on ne connaît plus les jours fériés (d'où un avertissement)
    ETAT["fin_feries"] = pd.to_datetime(feries["date"]).max().date()


def liberer_ressources():
    ETAT.clear()

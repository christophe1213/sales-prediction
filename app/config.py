"""Réglages de l'API : chemins des fichiers, version du modèle, limites.

Tout ce qui peut changer d'un environnement à l'autre (ton PC, Render...) est ici,
pour ne jamais avoir à fouiller dans le reste du code.
"""
import os
from pathlib import Path

# HORIZON et HISTORIQUE_MIN viennent de preparation.py (généré par le notebook) :
# ainsi l'API et l'entraînement partagent exactement les mêmes règles.
from .preparation import HISTORIQUE_MIN, HORIZON

# La racine du projet est le dossier qui contient "app/", "models/", "data/"...
RACINE = Path(__file__).resolve().parent.parent

VERSION = "v1"

CHEMIN_MODELE = RACINE / "models" / "model_final_v1.pkl"
CHEMIN_META_MODELE = RACINE / "models" / "model_final_v1_meta.json"
CHEMIN_META_DONNEES = RACINE / "processed" / "meta.json"
CHEMIN_MAGASINS = RACINE / "data" / "stores.csv"
CHEMIN_FERIES = RACINE / "data" / "holidays_events.csv"

# Exemple affiché dans Swagger (fabriqué par scripts/generer_exemple.py)
CHEMIN_EXEMPLE = RACINE / "exemples" / "data.json"

# Le rapport Evidently est lu depuis ce dossier (modifiable via une variable d'environnement)
DOSSIER_MONITORING = Path(os.getenv("DOSSIER_MONITORING", RACINE / "monitoring"))

__all__ = ["HISTORIQUE_MIN", "HORIZON", "VERSION", "RACINE", "CHEMIN_MODELE",
           "CHEMIN_META_MODELE", "CHEMIN_META_DONNEES", "CHEMIN_MAGASINS",
           "CHEMIN_FERIES", "CHEMIN_EXEMPLE", "DOSSIER_MONITORING"]

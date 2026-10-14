"""Exemple de requête affiché dans Swagger.

L'exemple n'est pas écrit à la main : il est fabriqué à partir des vraies ventes Favorita
par `scripts/generer_exemple.py`, puis simplement relu ici.
"""
import json
import logging

from .config import CHEMIN_EXEMPLE

journal = logging.getLogger("uvicorn.error")


def charger_exemple():
    """Renvoie l'exemple de requête, ou None si le fichier n'a pas encore été généré."""
    if not CHEMIN_EXEMPLE.is_file():
        journal.warning(
            "Pas d'exemple réel trouvé (%s). Lance `python scripts/generer_exemple.py` "
            "pour l'afficher dans Swagger.", CHEMIN_EXEMPLE)
        return None
    return json.loads(CHEMIN_EXEMPLE.read_text(encoding="utf-8"))

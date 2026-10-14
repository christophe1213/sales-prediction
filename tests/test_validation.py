"""Tests unitaires des règles de validation (app/validation.py).

Aucun modèle ni serveur nécessaire : ces tests sont rapides et tournent partout.
Lancement : pytest tests/test_validation.py -v
"""
import pandas as pd
import pytest

from app.config import HISTORIQUE_MIN, HORIZON
from app.schemas import Requete
from app.validation import EntreeInvalide, verifier_requete

from tests.donnees import DATE_DEBUT, corps_requete, faire_historique

# Mini tables de référence, juste ce dont la validation a besoin
REF = {"stores": pd.DataFrame(index=[1, 25])}
CATEGORIES = {"family": ["GROCERY I", "BEVERAGES"]}


def verifier(**surcharges):
    return verifier_requete(Requete(**corps_requete(**surcharges)), REF, CATEGORIES)


def test_requete_valide_renvoie_dates_et_historique():
    dates, historique = verifier()
    assert len(dates) == 7
    assert dates[0] == pd.Timestamp(DATE_DEBUT)
    assert len(historique) == 60


def test_promotions_facultatives():
    dates, _ = verifier(promotions=None)
    assert len(dates) == 7


@pytest.mark.parametrize("surcharges, message", [
    ({"store_nbr": 999}, "magasin inconnu"),
    ({"family": "PIZZA"}, "famille inconnue"),
    ({"promotions": [0, 0]}, "2 valeurs reçues, 7 attendues"),
    ({"promotions": [0, 0, -1, 0, 0, 0, 0]}, "négatives"),
    ({"historique": []}, "historique vide"),
    ({"historique": faire_historique(jours=30)}, "trop court"),
    ({"historique": faire_historique(ecart=0)}, "se terminer avant"),
    ({"historique": faire_historique(ecart=12)}, "horizon trop lointain"),
    ({"historique": faire_historique() + faire_historique()[-1:]}, "plusieurs fois"),
], ids=["magasin", "famille", "promos-nombre", "promos-negatives", "vide",
        "trop-court", "chevauche", "trop-loin", "doublon"])
def test_requete_refusee(surcharges, message):
    with pytest.raises(EntreeInvalide, match=message):
        verifier(**surcharges)


def test_limite_historique_minimum():
    """Exactement HISTORIQUE_MIN jours : accepté. Un jour de moins : refusé."""
    verifier(historique=faire_historique(jours=HISTORIQUE_MIN))
    with pytest.raises(EntreeInvalide, match="trop court"):
        verifier(historique=faire_historique(jours=HISTORIQUE_MIN - 1))


def test_limite_horizon():
    """Dernier jour prédit à exactement HORIZON jours du dernier jour connu : accepté."""
    # 7 jours prédits : le dernier est à (ecart + 6) jours de la fin de l'historique
    verifier(historique=faire_historique(ecart=HORIZON - 6))
    with pytest.raises(EntreeInvalide, match="horizon trop lointain"):
        verifier(historique=faire_historique(ecart=HORIZON - 5))

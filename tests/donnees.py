"""Petits outils pour fabriquer des requêtes de test.

Les ventes sont synthétiques : ces tests vérifient le fonctionnement de l'API
(validation, format, avertissements), pas la qualité des prévisions du modèle.
"""
import datetime as dt

DATE_DEBUT = dt.date(2017, 8, 16)


def faire_historique(date_debut=DATE_DEBUT, jours=60, ecart=1):
    """Ventes quotidiennes sur `jours` jours, la dernière tombant `ecart` jour(s) avant date_debut."""
    dernier_jour = date_debut - dt.timedelta(days=ecart)
    return [{"date": str(dernier_jour - dt.timedelta(days=i)), "sales": float(100 + (i % 7) * 10)}
            for i in range(jours - 1, -1, -1)]


def corps_requete(date_debut=DATE_DEBUT, nb_jours=7, **surcharges):
    """Corps JSON d'une requête valide. Passe un argument pour changer un champ,
    par exemple corps_requete(store_nbr=999) ou corps_requete(promotions=None)."""
    corps = {
        "store_nbr": 25,
        "family": "GROCERY I",
        "date_debut": str(date_debut),
        "nb_jours": nb_jours,
        "historique": faire_historique(date_debut),
        "promotions": [0.0] * nb_jours,
    }
    corps.update(surcharges)
    return corps

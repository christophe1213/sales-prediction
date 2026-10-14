"""Tests de l'API de prédiction des ventes, via un vrai client HTTP de test.

Ces tests ont besoin du modèle et des données (ils sont ignorés s'ils sont absents).
Lancement : pytest tests/ -v
"""
import datetime as dt

import pytest

from app.config import HORIZON

from tests.donnees import DATE_DEBUT, corps_requete, faire_historique


# --------------------------------------------------------------------- supervision
def test_health(client):
    reponse = client.get("/health")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["statut"] == "ok"
    assert corps["horizon_max_jours"] == HORIZON
    assert "rmsle_backtest" in corps


def test_options(client):
    reponse = client.get("/options")
    assert reponse.status_code == 200
    corps = reponse.json()
    assert 25 in corps["magasins"]
    assert "GROCERY I" in corps["familles"]
    assert len(corps["magasins"]) == 54 and len(corps["familles"]) == 33


# --------------------------------------------------------------------- /predict : cas normal
def test_predict_reponse_valide(client):
    reponse = client.post("/predict", json=corps_requete())
    assert reponse.status_code == 200
    corps = reponse.json()

    assert corps["store_nbr"] == 25 and corps["family"] == "GROCERY I"
    jours = [p["date"] for p in corps["predictions"]]
    assert jours == [str(DATE_DEBUT + dt.timedelta(days=i)) for i in range(7)]
    assert all(p["sales"] >= 0 for p in corps["predictions"])
    assert corps["total"] == pytest.approx(sum(p["sales"] for p in corps["predictions"]), abs=0.1)
    # Période de validation, promotions fournies : rien à signaler
    assert corps["avertissements"] == []


def test_predict_est_deterministe(client):
    premiere = client.post("/predict", json=corps_requete()).json()
    seconde = client.post("/predict", json=corps_requete()).json()
    assert premiere == seconde


# --------------------------------------------------------------------- /predict : avertissements
def test_avertissement_promotions_absentes(client):
    corps = client.post("/predict", json=corps_requete(promotions=None)).json()
    assert any("promotions non fournies" in a for a in corps["avertissements"])


def test_avertissement_periode_apres_2017(client):
    date_debut = dt.date(2026, 8, 16)
    requete = corps_requete(date_debut=date_debut)
    corps = client.post("/predict", json=requete).json()
    assert any("non validée" in a for a in corps["avertissements"])


def test_avertissement_decembre(client):
    requete = corps_requete(date_debut=dt.date(2017, 12, 10))
    corps = client.post("/predict", json=requete).json()
    assert any("décembre" in a for a in corps["avertissements"])


# --------------------------------------------------------------------- /predict : refus (422)
@pytest.mark.parametrize("surcharges, message", [
    ({"store_nbr": 999}, "magasin inconnu"),
    ({"family": "PIZZA"}, "famille inconnue"),
    ({"promotions": [0, 0]}, "promotions"),
    ({"historique": faire_historique(jours=30)}, "trop court"),
    ({"historique": faire_historique(ecart=0)}, "se terminer avant"),
], ids=["magasin", "famille", "promotions", "historique-court", "chevauche"])
def test_predict_refus_metier(client, surcharges, message):
    """Règle métier non respectée : 422 avec un message qui explique pourquoi."""
    reponse = client.post("/predict", json=corps_requete(**surcharges))
    assert reponse.status_code == 422
    assert message in reponse.json()["detail"]


@pytest.mark.parametrize("corps", [
    {"store_nbr": 1},                                          # champs manquants
    corps_requete(nb_jours=0, promotions=[]),                  # trop peu de jours
    corps_requete(nb_jours=HORIZON + 1, promotions=None),      # au-delà de l'horizon
    {**corps_requete(), "date_debut": "pas-une-date"},         # date illisible
    corps_requete(historique=[{"date": "2017-08-01", "sales": -5}]),  # vente négative
], ids=["champs-manquants", "zero-jour", "horizon-depasse", "date-illisible", "vente-negative"])
def test_predict_refus_de_forme(client, corps):
    """Requête mal formée : refusée par la validation du schéma (422)."""
    assert client.post("/predict", json=corps).status_code == 422


# --------------------------------------------------------------------- monitoring
def test_monitoring_rapport_absent(client, monkeypatch, tmp_path):
    monkeypatch.setattr("app.routes.monitoring.DOSSIER_MONITORING", tmp_path)
    assert client.get("/monitoring/derive").status_code == 404


def test_monitoring_rapport_present(client, monkeypatch, tmp_path):
    (tmp_path / "rapport_derive_test.html").write_text("<html>rapport</html>", encoding="utf-8")
    monkeypatch.setattr("app.routes.monitoring.DOSSIER_MONITORING", tmp_path)
    reponse = client.get("/monitoring/derive")
    assert reponse.status_code == 200
    assert "rapport" in reponse.text

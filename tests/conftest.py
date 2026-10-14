"""Fixtures partagées par tous les tests."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    """Client de test avec l'application réellement démarrée.

    Le `with` est indispensable : c'est lui qui déclenche le chargement du modèle
    (lifespan). Sans lui, les ressources ne seraient jamais chargées.
    Si le modèle ou les données sont absents, les tests qui en dépendent sont ignorés.
    """
    try:
        with TestClient(app) as c:
            yield c
    except (FileNotFoundError, RuntimeError) as erreur:
        pytest.skip(f"Démarrage impossible (modèle ou données manquants ?) : {erreur}")

# API de prédiction de ventes (Favorita)

## Structure

```
api_ventes/
├── app/
│   ├── main.py            # point d'entrée : crée l'app, branche les routes
│   ├── config.py          # chemins, version, limites
│   ├── ressources.py      # chargement du modèle au démarrage
│   ├── schemas.py         # requête / réponse, chaque champ documenté
│   ├── validation.py      # règles métier (lève EntreeInvalide -> 422)
│   ├── prevision.py       # appel du modèle + avertissements
│   ├── documentation.py   # textes Swagger
│   ├── exemples.py        # lit l'exemple réel
│   └── routes/            # prevision, supervision, monitoring
├── scripts/generer_exemple.py
├── exemples/exemple_reel.json   # généré (voir ci-dessous)
├── preparation.py         # généré par le notebook (inchangé, à la racine)
├── models/  processed/  data/  monitoring/
```

## Lancer

```bash
python scripts/generer_exemple.py      # une fois, pour l'exemple réel de Swagger
uvicorn app.main:app --reload          # puis ouvrir http://127.0.0.1:8000/docs
```

Sur Render, la commande de démarrage devient :
`uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

- `tests/test_validation.py` : règles de validation, sans modèle (rapide).
- `tests/test_api.py` : l'API démarrée pour de vrai (nécessite le modèle et `data/`, sinon ignoré).
- `tests/donnees.py` : fabrique des requêtes de test avec des ventes synthétiques.

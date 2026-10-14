"""Les textes affichés dans Swagger (/docs), séparés du code pour rester lisibles."""
from .config import HISTORIQUE_MIN, HORIZON

DESCRIPTION = f"""
Prévision des **ventes journalières** par magasin et par famille de produits,
sur **{HORIZON} jours au plus**.

### Domaine de validité
Le modèle (HistGradientBoosting, un seul modèle global) a été entraîné sur les données **Favorita**
(supermarchés d'Équateur, 2013-2017). Il ne connaît que les **54 magasins** et **33 familles**
de ce jeu (liste exacte : `GET /options`). Il n'est pas valable pour d'autres produits,
d'autres magasins ou d'autres pays.

### Comment l'utiliser
1. Consulte `GET /options` pour connaître les magasins et les familles acceptés.
2. Envoie à `POST /predict` l'historique récent des ventes **de la série visée**
   (un magasin, une famille).
3. Lis les `avertissements` de la réponse : ils signalent les limites de la prévision.

### Règles à connaître
- L'historique doit commencer au plus tard **{HISTORIQUE_MIN} jours** avant `date_debut`
  et se terminer **avant** `date_debut`.
- Le dernier jour prédit doit être à **{HORIZON} jours au plus** du dernier jour d'historique.
- Les promotions prévues sont facultatives, mais leur absence peut **sous-estimer** les ventes.
"""

TAGS = [
    {"name": "Prévision", "description": "Prédire les ventes des prochains jours."},
    {"name": "Supervision", "description": "État du service et valeurs acceptées."},
    {"name": "Monitoring", "description": "Rapports de suivi du modèle (dérive des données)."},
]

DESCRIPTION_PREDICT = f"""
Prédit les ventes quotidiennes d'**un magasin** pour **une famille de produits**.

Le service reconstruit lui-même les variables du modèle (retards de ventes, moyennes glissantes,
calendrier, jours fériés, informations du magasin) à partir de l'historique fourni.

**Refusé (erreur 422)** : magasin ou famille inconnus ; `nb_jours` hors de 1 à {HORIZON} ;
historique vide, en double, trop court, ou qui chevauche `date_debut` ; dernier jour prédit
trop éloigné du dernier jour d'historique ; nombre de promotions différent de `nb_jours`.

**Avertissements possibles** : promotions absentes ; jours fériés connus seulement jusqu'à fin 2017 ;
période postérieure à 2017 (non validée) ; décembre (erreur plus élevée).
"""

EXEMPLE_ERREUR_422 = {
    "detail": f"historique trop court : il doit commencer au plus tard le 2017-06-19 "
              f"({HISTORIQUE_MIN} jours avant date_debut), premier jour reçu : 2017-07-10"
}

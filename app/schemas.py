"""Ce que l'API reçoit (Requete) et ce qu'elle renvoie (Reponse).

Chaque champ a une description : c'est elle qui apparaît dans Swagger (/docs),
donc écris-la pour quelqu'un qui n'a jamais vu le notebook.
"""
import datetime as dt
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .config import HISTORIQUE_MIN, HORIZON
from .exemples import charger_exemple

_exemple = charger_exemple()


class Vente(BaseModel):
    """Les ventes d'une seule journée."""

    date: dt.date = Field(description="Le jour concerné, au format AAAA-MM-JJ.")
    sales: float = Field(
        ge=0,
        description="Nombre d'unités vendues ce jour-là (0 ou plus). Pas un chiffre d'affaires.")


class Requete(BaseModel):
    """Corps de la requête envoyée à POST /predict."""

    # Si l'exemple réel existe, Swagger le propose pré-rempli dans « Try it out ».
    model_config = ConfigDict(json_schema_extra={"examples": [_exemple]} if _exemple else {})

    store_nbr: int = Field(
        examples=[25],
        description="Numéro du magasin, de 1 à 54. La liste exacte est donnée par `GET /options`.")

    family: str = Field(
        examples=["GROCERY I"],
        description="Famille de produits, écrite **exactement** comme dans `GET /options` "
                    "(majuscules, espaces et chiffres romains compris).")

    date_debut: dt.date = Field(
        examples=["2017-08-16"],
        description="Premier jour à prédire (AAAA-MM-JJ). L'historique doit s'arrêter la veille "
                    "ou avant.")

    nb_jours: int = Field(
        ge=1, le=HORIZON, examples=[7],
        description=f"Combien de jours prédire à partir de `date_debut`, de 1 à {HORIZON}. "
                    f"Au-delà, la qualité de la prévision chute.")

    historique: list[Vente] = Field(
        description=(
            "Ventes quotidiennes passées **du même magasin et de la même famille**. "
            f"Le premier jour doit être au plus tard {HISTORIQUE_MIN} jours avant `date_debut`, "
            "et le dernier jour doit précéder `date_debut`. "
            "Si le magasin était fermé un jour, n'envoie simplement pas cette date. "
            "Une même date ne peut pas apparaître deux fois."))

    promotions: Optional[list[float]] = Field(
        default=None,
        description=(
            "Facultatif. Pour chaque jour à prédire, le **nombre d'articles de cette famille "
            "en promotion** dans le magasin (ce n'est ni un pourcentage de remise, ni un oui/non). "
            "Il faut autant de valeurs que `nb_jours`, dans l'ordre des dates, par exemple "
            "`[0, 0, 3, 0]` pour 4 jours avec 3 articles en promo le troisième jour. "
            "Sans cette liste, on suppose 0 partout et les ventes peuvent être sous-estimées."))


class PrevisionJour(BaseModel):
    date: dt.date = Field(description="Le jour prédit.")
    sales: float = Field(description="Ventes prévues, en unités (arrondies à 0,1).")


class Reponse(BaseModel):
    """Ce que renvoie POST /predict."""

    store_nbr: int = Field(description="Le magasin demandé.")
    family: str = Field(description="La famille demandée.")
    predictions: list[PrevisionJour] = Field(
        description="Une prévision par jour, dans l'ordre des dates.")
    total: float = Field(description="Somme des ventes prévues sur toute la période.")
    modele_version: str = Field(description="Version du modèle qui a fait la prévision.")
    avertissements: list[str] = Field(
        description="Les limites de cette prévision (promotions absentes, période non validée, "
                    "décembre...). Liste vide s'il n'y a rien à signaler.")
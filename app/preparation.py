import numpy as np
import pandas as pd

COLS_CAT = ["store_nbr", "family", "type_magasin", "cluster", "city", "state"]
HORIZON = 16          # jours de prévision maximum après le dernier jour connu
HISTORIQUE_MIN = 43   # jours d'historique nécessaires (moy_28 décalée de 16)


def preparer_references(stores, holidays_events):
    """Prépare une fois les infos magasins et les ensembles de jours fériés."""
    st = (stores.rename(columns={"type": "type_magasin"})
                .set_index("store_nbr")[["type_magasin", "cluster", "city", "state"]])
    h = holidays_events.copy()
    h["date"] = pd.to_datetime(h["date"])
    h = h[~h["transferred"]]
    conge = h[h["type"].isin(["Holiday", "Transfer", "Additional", "Bridge"])]
    nat = conge["locale"] == "National"
    reg = conge["locale"] == "Regional"
    loc = conge["locale"] == "Local"
    ev = (h["type"] == "Event") & (h["locale"] == "National")
    return {"stores": st,
            "nat": set(conge.loc[nat, "date"]),
            "reg": set(zip(conge.loc[reg, "date"], conge.loc[reg, "locale_name"])),
            "loc": set(zip(conge.loc[loc, "date"], conge.loc[loc, "locale_name"])),
            "ev": set(h.loc[ev, "date"])}


def construire_features(store_nbr, family, dates, historique, promotions, ref, categories, features):
    """Reconstruit les variables du modèle pour UNE série (magasin x famille).

    historique : ventes passées de la série (index = dates), au moins HISTORIQUE_MIN jours.
    promotions : nombre de produits en promotion pour chaque date à prédire.
                 Attention : si None, on suppose 0 promotion, ce qui peut sous-estimer les
                 ventes (en 2017, environ 46 % des lignes ont une promotion).
    """
    dates = pd.DatetimeIndex(dates)
    if store_nbr not in ref["stores"].index:
        raise ValueError(f"magasin inconnu : {store_nbr}")
    if family not in categories["family"]:
        raise ValueError(f"famille inconnue : {family}")
    info = ref["stores"].loc[store_nbr]

    h = pd.Series(historique, dtype="float64")
    h.index = pd.to_datetime(h.index)
    h = h.reindex(pd.date_range(h.index.min(), max(h.index.max(), dates.max()), freq="D"))
    decale = h.shift(16)

    X = pd.DataFrame({"date": dates})
    X["store_nbr"], X["family"] = store_nbr, family
    for c in ["type_magasin", "cluster", "city", "state"]:
        X[c] = info[c]
    X["onpromotion"] = (np.zeros(len(dates)) if promotions is None
                        else np.asarray(promotions, dtype=float)).astype("float32")
    X["lag_16"] = h.shift(16).reindex(dates).to_numpy()
    X["lag_21"] = h.shift(21).reindex(dates).to_numpy()
    X["lag_28"] = h.shift(28).reindex(dates).to_numpy()
    X["moy_7"] = decale.rolling(7, min_periods=4).mean().reindex(dates).to_numpy()
    X["moy_28"] = decale.rolling(28, min_periods=14).mean().reindex(dates).to_numpy()
    X["mois"], X["jour_semaine"] = dates.month, dates.dayofweek
    X["jour_annee"], X["jour_du_mois"] = dates.dayofyear, dates.day
    X["ferie_national"] = [int(d in ref["nat"]) for d in dates]
    reg = [(d, info["state"]) in ref["reg"] for d in dates]
    loc = [(d, info["city"]) in ref["loc"] for d in dates]
    X["est_ferie"] = [int(a or b or c) for a, b, c in zip(X["ferie_national"], reg, loc)]
    X["evenement_national"] = [int(d in ref["ev"]) for d in dates]
    for c in COLS_CAT:
        X[c] = pd.Categorical(X[c], categories=categories[c])
    return X[features]

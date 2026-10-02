"""Summary tables by town and neighborhood, and the check against the published figure."""
import pandas as pd

# Class limits printed on the published map (Silveira, Faccin, Detoni & Silva, 2024, figure of census tracts)
PUBLISHED = {"residents_min": 3, "residents_max": 1229, "residents_per_dwelling_min": 2.0, "residents_per_dwelling_max": 4.5}


def by_town(t):
    u = t.assign(urban=t["situation"].eq("URBANO"))
    g = u.groupby(["town", "urban"]).agg(tracts=("tract", "size"), residents=("residents", "sum")).unstack(fill_value=0)
    out = pd.DataFrame({"tracts": g["tracts"].sum(axis=1), "residents": g["residents"].sum(axis=1),
                        "urban_residents": g["residents"][True]})
    out["urban_pct"] = 100 * out["urban_residents"] / out["residents"]
    urb = u[u["urban"]]
    w = urb["residents"]
    out["income_mw_urban"] = (urb["income_mw"] * w).groupby(urb["town"]).sum() / w.groupby(urb["town"]).sum()
    return out.reset_index()


def by_neighborhood(t, nb):
    u = t[t["situation"].eq("URBANO")]
    w = u["residents"].fillna(0)
    g = u.assign(w=w, wi=u["income_mw"] * w, wd=u["residents_per_dwelling"] * w).groupby(["town", "neighborhood"])
    out = g.agg(tracts=("tract", "size"), residents=("w", "sum"), wi=("wi", "sum"), wd=("wd", "sum"))
    out["income_mw"] = out["wi"] / out["residents"]
    out["residents_per_dwelling"] = out["wd"] / out["residents"]
    return out.drop(columns=["wi", "wd"]).reset_index()


def compare(t):
    computed = {"residents_min": t["residents"].min(), "residents_max": t["residents"].max(),
                "residents_per_dwelling_min": t["residents_per_dwelling"].min(),
                "residents_per_dwelling_max": t["residents_per_dwelling"].max()}
    return pd.DataFrame([{"item": k, "published": v, "computed": round(float(computed[k]), 2)} for k, v in PUBLISHED.items()])

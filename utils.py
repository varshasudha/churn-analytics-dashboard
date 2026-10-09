"""Shared data loading, segmentation, filters and KPI helpers."""
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "European_Bank.csv"
ORDERS = {
    "AgeGroup": ["<30", "30-45", "46-60", "60+"],
    "CreditBand": ["Low", "Medium", "High"],
    "TenureGroup": ["New (0-2)", "Mid-term (3-6)", "Long-term (7-10)"],
    "BalanceSeg": ["Zero", "Low", "High"],
    "Geography": ["France", "Germany", "Spain"],
}
LABELS = {"Geography": "Geography", "Gender": "Gender", "AgeGroup": "Age group",
          "CreditBand": "Credit band", "TenureGroup": "Tenure group",
          "BalanceSeg": "Balance segment", "Activity": "Activity",
          "NumOfProducts": "Products held"}


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH).drop(columns=["Year", "Surname"], errors="ignore")
    df["AgeGroup"] = pd.cut(df.Age, [0, 29, 45, 60, 200], labels=ORDERS["AgeGroup"]).astype(str)
    df["CreditBand"] = pd.cut(df.CreditScore, [0, 579, 739, 900], labels=ORDERS["CreditBand"]).astype(str)
    df["TenureGroup"] = pd.cut(df.Tenure, [-1, 2, 6, 10], labels=ORDERS["TenureGroup"]).astype(str)
    med = df.loc[df.Balance > 0, "Balance"].median()
    df["BalanceSeg"] = np.where(df.Balance == 0, "Zero", np.where(df.Balance < med, "Low", "High"))
    df["HighValue"] = (df.Balance >= df.Balance.quantile(0.75)).astype(int)  # fixed on full data
    df["Activity"] = df.IsActiveMember.map({1: "Active", 0: "Inactive"})
    df["Status"] = df.Exited.map({1: "Churned", 0: "Retained"})
    return df


def setup(title):
    st.set_page_config(page_title=title, page_icon="🏦", layout="wide")
    st.title(title)


def sidebar_filters(df):
    """Keyed widgets -> selections persist across pages via st.session_state."""
    st.sidebar.header("Segment filters")
    mask = pd.Series(True, index=df.index)
    for col in ["Geography", "Gender", "AgeGroup", "CreditBand", "TenureGroup", "BalanceSeg", "Activity"]:
        opts = ORDERS.get(col) or sorted(df[col].unique())
        sel = st.sidebar.multiselect(LABELS[col], opts, default=opts, key=f"flt_{col}")
        mask &= df[col].isin(sel)
    prods = sorted(df.NumOfProducts.unique())
    sel = st.sidebar.multiselect("Products held", prods, default=prods, key="flt_NumOfProducts")
    mask &= df.NumOfProducts.isin(sel)
    out = df[mask]
    st.sidebar.caption(f"{len(out):,} of {len(df):,} customers selected")
    if out.empty:
        st.warning("No customers match the current filters. Widen the selection in the sidebar.")
        st.stop()
    return out


def kpis(df):
    ov = df.Exited.mean()
    hv, nhv = df[df.HighValue == 1], df[df.HighValue == 0]
    ina, act = df[df.Activity == "Inactive"], df[df.Activity == "Active"]
    hv_ratio = hv.Exited.mean() / nhv.Exited.mean() if len(hv) and len(nhv) and nhv.Exited.mean() > 0 else np.nan
    eng = ina.Exited.mean() / act.Exited.mean() if len(ina) and len(act) and act.Exited.mean() > 0 else np.nan
    bal_total = df.Balance.sum()
    return {"overall": ov * 100, "customers": len(df), "churned": int(df.Exited.sum()),
            "hv_ratio": hv_ratio, "hv_churn": hv.Exited.mean() * 100 if len(hv) else np.nan,
            "eng_ratio": eng, "bal_at_risk": df.loc[df.Exited == 1, "Balance"].sum(),
            "bal_share": df.loc[df.Exited == 1, "Balance"].sum() / bal_total * 100 if bal_total else np.nan}


def churn_by(df, col):
    g = df.groupby(col).agg(Customers=("Exited", "size"), Churned=("Exited", "sum")).reset_index()
    g["Churn %"] = (g.Churned / g.Customers * 100).round(2)
    g["Share of churn %"] = (g.Churned / max(g.Churned.sum(), 1) * 100).round(2)
    g["Risk index"] = (g["Churn %"] / (df.Exited.mean() * 100)).round(2) if df.Exited.mean() > 0 else np.nan
    if col in ORDERS:
        g[col] = pd.Categorical(g[col], ORDERS[col], ordered=True)
        g = g.sort_values(col)
    return g


def bar(g, col, title, y="Churn %"):
    f = px.bar(g, x=col, y=y, text=y, title=title, hover_data=["Customers", "Churned"],
               color=y, color_continuous_scale="Reds")
    f.update_traces(textposition="outside")
    f.update_layout(coloraxis_showscale=False, yaxis_title=y, height=380)
    return f


def fmt_m(x):
    return f"{x/1e6:,.1f}M"


def kpi_row(k):
    c = st.columns(5)
    c[0].metric("Overall churn rate", f"{k['overall']:.2f}%", f"{k['churned']:,} of {k['customers']:,}", delta_color="off")
    c[1].metric("High-value churn ratio", "n/a" if np.isnan(k["hv_ratio"]) else f"{k['hv_ratio']:.2f}x")
    c[2].metric("Engagement drop indicator", "n/a" if np.isnan(k["eng_ratio"]) else f"{k['eng_ratio']:.2f}x")
    c[3].metric("Balance at risk", fmt_m(k["bal_at_risk"]))
    c[4].metric("Share of balance at risk", f"{k['bal_share']:.1f}%")

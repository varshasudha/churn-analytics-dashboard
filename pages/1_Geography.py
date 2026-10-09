import plotly.express as px
import streamlit as st
from utils import load_data, setup, sidebar_filters, churn_by, bar, fmt_m

setup("Geography-wise churn")
df = sidebar_filters(load_data())
g = churn_by(df, "Geography")
c1, c2 = st.columns(2)
c1.plotly_chart(bar(g, "Geography", "Churn rate by country"), width="stretch")
c2.plotly_chart(bar(g, "Geography", "Share of all churners by country (%)", y="Share of churn %"), width="stretch")
st.subheader("Geographic Risk Index (country churn / overall churn)")
cols = st.columns(len(g))
for col, (_, r) in zip(cols, g.iterrows()):
    col.metric(str(r.Geography), f"{r['Risk index']:.2f}", f"{r['Churn %']:.2f}% churn", delta_color="off")
st.subheader("Geography x segment interaction")
other = st.selectbox("Cross with", ["AgeGroup", "Gender", "Activity", "BalanceSeg", "CreditBand", "TenureGroup"])
pv = df.pivot_table(index="Geography", columns=other, values="Exited", aggfunc="mean") * 100
st.plotly_chart(px.imshow(pv.round(1), text_auto=True, color_continuous_scale="Reds", aspect="auto",
                          labels=dict(color="Churn %")), width="stretch")
bal = df[df.Exited == 1].groupby("Geography").Balance.sum().reset_index()
bal["Balance at risk"] = bal.Balance.map(fmt_m)
st.dataframe(bal[["Geography", "Balance at risk"]], hide_index=True)

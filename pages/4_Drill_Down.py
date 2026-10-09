import plotly.express as px
import streamlit as st
from utils import load_data, setup, sidebar_filters, churn_by, LABELS

setup("Segment drill-down & profile comparison")
df = sidebar_filters(load_data())
dims = ["Geography", "Gender", "AgeGroup", "CreditBand", "TenureGroup", "BalanceSeg", "Activity", "NumOfProducts"]
a, b = st.columns(2)
d1 = a.selectbox("Primary segment", dims, index=0)
d2 = b.selectbox("Drill into", [d for d in dims if d != d1], index=1)
v = st.selectbox(f"Focus on one {LABELS[d1]} value", ["All"] + sorted(df[d1].astype(str).unique()))
sub = df if v == "All" else df[df[d1].astype(str) == v]
st.write(f"**{len(sub):,} customers**, churn rate **{sub.Exited.mean()*100:.2f}%**")
st.dataframe(churn_by(sub, d2), hide_index=True, width="stretch")
pv = df.pivot_table(index=d1, columns=d2, values="Exited", aggfunc="mean") * 100
st.plotly_chart(px.imshow(pv.round(1), text_auto=True, color_continuous_scale="Reds", aspect="auto",
                          title=f"Churn % : {LABELS[d1]} x {LABELS[d2]}"), width="stretch")
st.subheader("Churned vs retained profile")
prof = df.groupby("Status")[["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary"]].mean().round(1).T
st.dataframe(prof, width="stretch")

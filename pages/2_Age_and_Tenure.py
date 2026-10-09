import pandas as pd
import plotly.express as px
import streamlit as st
from utils import load_data, setup, sidebar_filters, churn_by, bar

setup("Age & tenure churn comparison")
df = sidebar_filters(load_data())
c1, c2 = st.columns(2)
c1.plotly_chart(bar(churn_by(df, "AgeGroup"), "AgeGroup", "Churn rate by age group"), width="stretch")
c2.plotly_chart(bar(churn_by(df, "TenureGroup"), "TenureGroup", "Churn rate by tenure group"), width="stretch")
bins = pd.cut(df.Age, [17, 25, 30, 35, 40, 45, 50, 55, 60, 65, 100]).astype(str)
line = df.groupby(bins).Exited.agg(["mean", "size"]).reset_index()
line["Churn %"] = (line["mean"] * 100).round(1)
line = line.sort_values("Age", key=lambda s: s.str.extract(r"\((\d+)")[0].astype(int))
st.plotly_chart(px.line(line, x="Age", y="Churn %", markers=True, hover_data=["size"], title="Churn rate by 5-year age band"),
                width="stretch")
st.subheader("Age x tenure")
pv = df.pivot_table(index="AgeGroup", columns="TenureGroup", values="Exited", aggfunc="mean") * 100
pv = pv.reindex(index=[i for i in ["<30", "30-45", "46-60", "60+"] if i in pv.index])
st.plotly_chart(px.imshow(pv.round(1), text_auto=True, color_continuous_scale="Reds", aspect="auto"), width="stretch")
st.caption("Small cells (e.g. age 60+) have few customers; treat their rates with caution.")

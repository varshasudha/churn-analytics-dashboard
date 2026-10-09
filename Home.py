import plotly.express as px
import streamlit as st
from utils import load_data, setup, sidebar_filters, kpis, kpi_row, churn_by, bar

setup("Customer Segmentation & Churn Analytics - European Banking")
st.caption("Varsha Sudha | Machine Learning Intern, Unified Mentor")
df = sidebar_filters(load_data())
kpi_row(kpis(df))
st.divider()
a, b = st.columns([1, 2])
pie = px.pie(df.groupby("Status").size().reset_index(name="n"), names="Status", values="n", hole=0.55,
             color="Status", color_discrete_map={"Churned": "#d62728", "Retained": "#1f77b4"}, title="Churned vs retained")
pie.update_layout(height=380)
a.plotly_chart(pie, width="stretch")
dim = b.selectbox("Segment churn rate by", ["Geography", "Gender", "AgeGroup", "CreditBand", "TenureGroup",
                                            "BalanceSeg", "Activity", "NumOfProducts"])
g = churn_by(df, dim)
b.plotly_chart(bar(g, dim, f"Churn rate by {dim}"), width="stretch")
st.dataframe(g, width="stretch", hide_index=True)
st.info("Use the sidebar filters (they apply to every page) and the pages menu for geography, age/tenure, "
        "high-value and drill-down views.")

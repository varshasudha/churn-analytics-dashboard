import plotly.express as px
import streamlit as st
from utils import load_data, setup, sidebar_filters, churn_by, bar, fmt_m

setup("High-value customer churn explorer")
full = load_data()
thr = full.loc[full.HighValue == 1, "Balance"].min()
st.caption(f"High-value = balance of at least {thr:,.0f} (top 25% of all customers).")
df = sidebar_filters(full)
hv = df[df.HighValue == 1]
if hv.empty:
    st.warning("No high-value customers in the current selection."); st.stop()
c = st.columns(4)
c[0].metric("High-value customers", f"{len(hv):,}")
c[1].metric("High-value churn rate", f"{hv.Exited.mean()*100:.2f}%")
c[2].metric("Other customers churn rate", f"{df[df.HighValue==0].Exited.mean()*100:.2f}%" if (df.HighValue == 0).any() else "n/a")
c[3].metric("High-value balance at risk", fmt_m(hv.loc[hv.Exited == 1, "Balance"].sum()))
d = st.selectbox("Break down high-value churn by", ["Geography", "AgeGroup", "Activity", "Gender", "NumOfProducts"])
st.plotly_chart(bar(churn_by(hv, d), d, f"High-value churn by {d}"), width="stretch")
lo, hi = float(df.Balance.min()), float(df.Balance.max())
rng = st.slider("Balance range explorer", lo, hi, (lo, hi))
ex = df[df.Balance.between(*rng)]
sc = px.scatter(ex.sample(min(len(ex), 3000), random_state=1), x="EstimatedSalary", y="Balance", color="Status",
                color_discrete_map={"Churned": "#d62728", "Retained": "#1f77b4"}, opacity=0.6, title="Salary vs balance")
st.plotly_chart(sc, width="stretch")
st.write(f"Churn rate in selected balance range: **{ex.Exited.mean()*100:.2f}%** ({len(ex):,} customers)")
st.subheader("Largest high-value churners")
st.dataframe(hv[hv.Exited == 1].nlargest(20, "Balance")[["CustomerId", "Geography", "Gender", "Age", "Balance",
             "EstimatedSalary", "NumOfProducts", "Activity"]], hide_index=True, width="stretch")

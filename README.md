# Customer Segmentation & Churn Pattern Analytics in European Banking

Streamlit dashboard built for Unified Mentor by **Varsha Sudha** (Machine Learning Intern).

**Live Demo:** _add your Streamlit link here_

## Pages
- **Home** - overall churn summary and KPIs (overall churn, high-value churn ratio, engagement drop, balance at risk)
- **Geography** - country churn, Geographic Risk Index, geography x segment heatmaps
- **Age and Tenure** - churn by age group, tenure group and 5-year age band
- **High-Value Customers** - top-25%-by-balance churn explorer
- **Drill Down** - any segment x segment view and churned vs retained profile

Sidebar filters (geography, gender, age, credit, tenure, balance, activity, products) apply to every page.

## Segment definitions
Age: <30, 30-45, 46-60, 60+ | Credit: Low <580, Medium 580-739, High >=740 | Tenure: New 0-2, Mid 3-6, Long 7-10 |
Balance: Zero, Low/High split at median of non-zero balances | High-value: top 25% by balance.

## Run locally
```
pip install -r requirements.txt
streamlit run Home.py
```
Data: `data/European_Bank.csv` (10,000 customers). Balance is a proxy for value; the dataset has no revenue or date field.

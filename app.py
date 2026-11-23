import streamlit as st
import pandas as pd

from src.quality_analysis import load_and_validate, capability_summary, defect_analysis

st.set_page_config(page_title="Injection Moulding Quality Analysis", layout="wide")
st.title("Injection Moulding Defects & Dimensional Quality Dashboard")

uploaded = st.sidebar.file_uploader("Upload inspection CSV", type="csv")
data_path = uploaded if uploaded is not None else "data/plastic_components.csv"

try:
    df = load_and_validate(data_path)
except Exception as exc:
    st.error(str(exc))
    st.stop()

st.sidebar.header("Filters")
machines = st.sidebar.multiselect("Machine", sorted(df["Machine"].unique()), default=[])
materials = st.sidebar.multiselect("Material", sorted(df["Material"].unique()), default=[])
filtered = df.copy()
if machines:
    filtered = filtered[filtered["Machine"].isin(machines)]
if materials:
    filtered = filtered[filtered["Material"].isin(materials)]

col1, col2, col3 = st.columns(3)
col1.metric("Observations", len(filtered))
col2.metric("Batches", filtered["Batch_ID"].nunique())
col3.metric("Defects", int(filtered["Defect_Count"].sum()))

st.subheader("Defect Pareto")
defects = defect_analysis(filtered)
st.bar_chart(defects["count"])

st.subheader("Dimensional Process Capability")
capability = capability_summary(filtered)
st.dataframe(pd.DataFrame(capability).T)

st.subheader("Dimensional Measurements")
selected = st.selectbox("Dimension", ["Length_mm", "Width_mm", "Thickness_mm", "Diameter_mm"])
st.histogram(filtered[selected], bins=20)

st.subheader("Data preview")
st.dataframe(filtered.head(100), use_container_width=True)

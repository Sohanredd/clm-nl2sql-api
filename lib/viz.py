import streamlit as st
import pandas as pd

def bar_chart(df, col):
    counts = df[col].value_counts().head(10)
    st.bar_chart(counts)

def pie_chart(df, col):
    counts = df[col].value_counts()
    st.write("Pie/Donut Chart")
    st.write(counts)
    st.pyplot()

def timeseries_chart(df, dt_col):
    df[dt_col] = pd.to_datetime(df[dt_col], errors='coerce')
    ts = df.groupby(df[dt_col].dt.date).size()
    st.line_chart(ts)

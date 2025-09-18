import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px

def pick_chart(df: pd.DataFrame):
    try:
        if df.empty:
            st.info("No data to display.")
            return None
        cols = df.columns.tolist()
        # If SourceTable column exists, group and plot by SourceTable
        if "SourceTable" in cols:
            for table in df["SourceTable"].unique():
                st.subheader(f"Source: {table}")
                subdf = df[df["SourceTable"] == table]
                subcols = [c for c in subdf.columns if c != "SourceTable"]
                if len(subcols) == 2 and pd.api.types.is_numeric_dtype(subdf[subcols[1]]):
                    chart = alt.Chart(subdf).mark_bar().encode(x=subcols[0], y=subcols[1])
                    st.altair_chart(chart, use_container_width=True)
                elif any(pd.api.types.is_datetime64_any_dtype(subdf[c]) for c in subcols) and len(subcols) >= 2:
                    date_col = next(c for c in subcols if pd.api.types.is_datetime64_any_dtype(subdf[c]))
                    metric_col = next(c for c in subcols if c != date_col and pd.api.types.is_numeric_dtype(subdf[c]))
                    chart = alt.Chart(subdf).mark_line().encode(x=date_col, y=metric_col)
                    st.altair_chart(chart, use_container_width=True)
                elif sum(pd.api.types.is_numeric_dtype(subdf[c]) for c in subcols) == 2 and len(subdf) <= 5000:
                    num_cols = [c for c in subcols if pd.api.types.is_numeric_dtype(subdf[c])]
                    fig = px.scatter(subdf, x=num_cols[0], y=num_cols[1])
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(subdf)
        else:
            if len(cols) == 2 and pd.api.types.is_numeric_dtype(df[cols[1]]):
                chart = alt.Chart(df).mark_bar().encode(x=cols[0], y=cols[1])
                st.altair_chart(chart, use_container_width=True)
            elif any(pd.api.types.is_datetime64_any_dtype(df[c]) for c in cols) and len(cols) >= 2:
                date_col = next(c for c in cols if pd.api.types.is_datetime64_any_dtype(df[c]))
                metric_col = next(c for c in cols if c != date_col and pd.api.types.is_numeric_dtype(df[c]))
                chart = alt.Chart(df).mark_line().encode(x=date_col, y=metric_col)
                st.altair_chart(chart, use_container_width=True)
            elif sum(pd.api.types.is_numeric_dtype(df[c]) for c in cols) == 2 and len(df) <= 5000:
                num_cols = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
                fig = px.scatter(df, x=num_cols[0], y=num_cols[1])
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.dataframe(df)
    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.dataframe(df)

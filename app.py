import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2


DB_PARAMS = {
    "dbname": "szpital_z07",
    "user": "admin",
    "password": "password",
    "host": "localhost",
    "port": "5432"
}


@st.cache_data
def query_db(sql):
    connection = psycopg2.connect(**DB_PARAMS)
    df = pd.read_sql(sql, connection)
    connection.close()
    return df


st.set_page_config(layout="wide", page_title="Szpital")

st.header("Demografia pacjentów")
col1, col2 = st.columns(2)
with col1:
    gender = query_db("SELECT gender, COUNT(*) AS count FROM patients GROUP BY gender")
    fig = px.pie(gender, names="gender", values="count", title="Rozkład płci pacjentów")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    race = query_db("SELECT race, COUNT(*) AS count FROM patients GROUP BY race")
    fig = px.bar(race, x="race", y="count", title="Rozkład rasowy pacjentów")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Mapa lokalizacji pacjentów")
locations = query_db("SELECT lat, lon FROM patients WHERE lat IS NOT NULL AND lon IS NOT NULL")
st.map(locations, zoom=6)

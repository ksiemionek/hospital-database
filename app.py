import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import uuid
from datetime import date


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

st.subheader("Dodaj nowego pacjenta")

with st.form("add_patient"):
    first_name = st.text_input("Imię", max_chars=30)
    last_name = st.text_input("Nazwisko", max_chars=30)
    gender = st.selectbox("Płeć", {"Kobieta": "F", "Mężczyzna": "M"})
    race = st.text_input("Rasa", max_chars=10)
    ethnicity = st.text_input("Etniczność", max_chars=20)
    birthdate = st.date_input("Data urodzenia", max_value=date.today())
    ssn = st.text_input("Numer SSN", max_chars=11)
    lat = st.number_input("Szerokość geograficzna", format="%.6f", step=0.000001)
    lon = st.number_input("Długość geograficzna", format="%.6f", step=0.000001)
    submitted = st.form_submit_button("Dodaj pacjenta")

    if submitted:
            if not all([first_name, last_name, race, ethnicity, ssn]):
                st.warning("Proszę uzupełnić wszystkie dane pacjenta! >:(")
            else:
                conn = psycopg2.connect(**DB_PARAMS)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO patients (
                        id, birthdate, ssn, first, last,
                        gender, race, ethnicity, lat, lon
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()), birthdate, ssn, first_name, last_name,
                    gender, race, ethnicity,
                    lat if lat != 0 else None, lon if lon != 0 else None
                ))
                conn.commit()
                cur.close()
                conn.close()
                st.success("Pacjent został dodany.")

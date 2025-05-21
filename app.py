import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import uuid
import datetime


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

# ===========================================================
#                         STATYSTYKI
# ===========================================================
st.header("STATYSTYKI")
st.subheader("Demografia pacjentów")
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

st.subheader("Najczęstsze diagnozy pacjentów")
conditions = query_db("""
    SELECT description, COUNT(*) AS count
    FROM conditions
    WHERE description LIKE '%(disorder)'
    GROUP BY description
    ORDER BY count DESC
    LIMIT 20
""")
if conditions.empty:
    st.info("Brak diagnoz.")
else:
    fig = px.bar(conditions, x="description", y="count",
                 title="Diagnozy", labels={"count": "Liczba przypadków", "description": "Diagnoza"})
    st.plotly_chart(fig, use_container_width=True)

# ===========================================================
#                         PACJENCI
# ===========================================================
st.header("PACJENCI")
# -----------------------------------------------
#                Dodawanie pacjentów
# -----------------------------------------------

if "show_add_patient" not in st.session_state:
    st.session_state.show_add_patient = False
def toggle_add_patient():
    st.session_state.show_add_patient = not st.session_state.show_add_patient

st.button("Dodaj pacjenta", on_click=toggle_add_patient)

if st.session_state.show_add_patient:
    with st.form("add_patient"):
        first_name = st.text_input("Imię", max_chars=30)
        last_name = st.text_input("Nazwisko", max_chars=30)
        gender_options = {"Kobieta": "F", "Mężczyzna": "M"}
        gender_display = st.selectbox("Płeć", options=list(gender_options.keys()))
        gender = gender_options[gender_display]
        race = st.text_input("Rasa", max_chars=10)
        ethnicity = st.text_input("Etniczność", max_chars=20)
        birthdate = st.date_input(
            "Data urodzenia",
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today()
        )
        ssn = st.text_input("Numer SSN", max_chars=11)
        lat = st.number_input("Szerokość geograficzna", format="%.6f", step=0.000001)
        lon = st.number_input("Długość geograficzna", format="%.6f", step=0.000001)
        submitted = st.form_submit_button("Dodaj pacjenta")

        if submitted:
            if not all([first_name, last_name, race, ethnicity, ssn]):
                st.warning("Proszę uzupełnić wszystkie dane pacjenta!")
            else:
                try:
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
                    st.session_state.show_add_patient = False
                except Exception as e:
                    st.error(f"Wystąpił błąd!\n{e}")

# -----------------------------------------------
#              Wyświetlanie pacjentów
# -----------------------------------------------

if "show_patients_list" not in st.session_state:
    st.session_state.show_patients_list = False
def toggle_show_patients():
    st.session_state.show_patients_list = not st.session_state.show_patients_list

if st.button("Wyświetl pacjentów", on_click=toggle_show_patients):
    pass

if st.session_state.show_patients_list:
    patients_df = query_db("SELECT id, ssn, last, first FROM patients ORDER BY id")
    patients_per_page = 50
    total_pages = (len(patients_df) - 1) // patients_per_page + 1

    if patients_df.empty:
        st.info("Brak pacjentów.")
    else:
        st.write("### Lista pacjentów:")
        page = st.number_input("Strona", min_value=1, max_value=total_pages, step=1, value=1)
        start_idx = (page - 1) * patients_per_page
        end_idx = start_idx + patients_per_page

        for index, row in patients_df.iloc[start_idx:end_idx].iterrows():
            with st.expander(f"SSN: {row['ssn']} - {row['last']} {row['first']}"):
                details = query_db(f"""
                    SELECT birthdate, gender, race, ethnicity, lat, lon, ssn
                    FROM patients
                    WHERE id = '{row['id']}'
                """)
                st.write("**Numer SSN:**", details.at[0, "ssn"])
                st.write("**Data urodzenia:**", details.at[0, "birthdate"])
                st.write("**Płeć:**", details.at[0, "gender"])
                st.write("**Rasa:**", details.at[0, "race"])
                st.write("**Etniczność:**", details.at[0, "ethnicity"])
                st.write("**Lokalizacja:**", f"{details.at[0, 'lat']}, {details.at[0, 'lon']}")

                diagnoses = query_db(f"""
                           SELECT description 
                           FROM conditions
                           WHERE patient = '{row['id']}' AND description LIKE '%(disorder)'
                           ORDER BY start DESC
                           LIMIT 10
                       """)

                if diagnoses.empty:
                    st.write("**Diagnozy:** brak.")
                else:
                    st.write("**Diagnozy:**")
                    for desc in diagnoses['description']:
                        st.write(f"- {desc}")

# ===========================================================
#                         ZAPASY
# ===========================================================
st.header("MAGAZYN SZPITALA")

# -----------------------------------------------
#              Wyświetlanie leków
# -----------------------------------------------

if "show_medications" not in st.session_state:
    st.session_state.show_medications = False
def toggle_medications():
    st.session_state.show_medications = not st.session_state.show_medications

if st.button("Wyświetl zapasy leków", on_click=toggle_medications):
    pass

if st.session_state.show_medications:
    st.subheader("Dostępne leki")

    medications_summary = query_db("""
        SELECT description, SUM(dispenses) AS total_dispenses
        FROM medications
        GROUP BY description
        ORDER BY total_dispenses DESC
    """)

    if medications_summary.empty:
        st.info("Brak danych.")
    else:
        meds_display = medications_summary.rename(columns={
            "description": "Nazwa leku",
            "total_dispenses": "Łączna liczba dawek",
        })
        st.dataframe(meds_display, use_container_width=True)

# -----------------------------------------------
#              Wyświetlanie zapasów
# -----------------------------------------------
if "show_supplies" not in st.session_state:
    st.session_state.show_supplies = False

def toggle_supplies():
    st.session_state.show_supplies = not st.session_state.show_supplies

if st.button("Wyświetl materiały medyczne", on_click=toggle_supplies):
    pass

if st.session_state.show_supplies:
    st.header("Dostępne materiały medyczne")

    supplies_summary = query_db("""
        SELECT description, SUM(quantity) AS total_quantity
        FROM supplies
        GROUP BY description
        ORDER BY total_quantity DESC
        LIMIT 20
    """)

    if supplies_summary.empty:
        st.info("Brak danych.")
    else:
        supplies_display = supplies_summary.rename(columns={
            "description": "Nazwa materiału",
            "total_quantity": "Łączna liczba"
        })
        st.dataframe(supplies_display, use_container_width=True)

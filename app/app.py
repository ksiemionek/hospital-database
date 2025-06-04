import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
import uuid
import datetime


# =============================
#        CONFIG & DB
# =============================

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


# =============================
#        PAGE SETTINGS
# =============================

st.set_page_config(layout="wide", page_title="Szpital")


# =============================
#         STATISTICS
# =============================


def render_statistics():
    st.header("STATYSTYKI")

    st.subheader("Demografia pacjentów")
    col1, col2 = st.columns(2)

    with col1:
        gender = query_db("SELECT * FROM get_gender_distribution()")
        fig = px.pie(gender, names="gender", values="count", title="Rozkład płci pacjentów")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        race = query_db("SELECT * FROM get_race_distribution()")
        fig = px.bar(race, x="race", y="count", title="Rozkład rasowy pacjentów")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Mapa lokalizacji pacjentów")
    locations = query_db("SELECT * FROM get_patient_locations()")
    st.map(locations, zoom=6)

    st.subheader("Najczęstsze diagnozy pacjentów")
    conditions = query_db("SELECT * FROM get_top_diagnoses()")
    if conditions.empty:
        st.info("Brak diagnoz.")
    else:
        fig = px.bar(
            conditions,
            x="description",
            y="count",
            title="Diagnozy",
            labels={"count": "Liczba przypadków", "description": "Diagnoza"}
        )
        st.plotly_chart(fig, use_container_width=True)


# =============================
#           PATIENTS
# =============================


def render_patient_section():
    st.header("PACJENCI")

    render_add_patient()
    render_patient_list()


def render_add_patient():
    if "show_add_patient" not in st.session_state:
        st.session_state.show_add_patient = False

    if st.button("Dodaj pacjenta"):
        st.session_state.show_add_patient = not st.session_state.show_add_patient

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
                    add_patient_to_db(
                        first_name, last_name, gender, race, ethnicity, birthdate, ssn, lat, lon
                    )


def add_patient_to_db(first_name, last_name, gender, race, ethnicity, birthdate, ssn, lat, lon):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CALL add_patient(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    str(uuid.uuid4()), birthdate, ssn, first_name, last_name,
                    gender, race, ethnicity,
                    lat if lat != 0 else None,
                    lon if lon != 0 else None
                ])
        st.success("Pacjent został dodany.")
        st.session_state.show_add_patient = False
    except Exception as e:
        st.error(f"Wystąpił błąd!\n{e}")


def render_patient_list():
    if "show_patients_list" not in st.session_state:
        st.session_state.show_patients_list = False

    if st.button("Wyświetl pacjentów"):
        st.session_state.show_patients_list = not st.session_state.show_patients_list

    if st.session_state.show_patients_list:
        st.write("### Lista pacjentów:")
        search_term = st.text_input("Wyszukaj pacjenta:").strip()
        patients_df = (
            query_db(f"SELECT * FROM search_patients('{search_term}')")
            if search_term
            else query_db("SELECT * FROM get_all_patients()")
        )

        patients_per_page = 50
        total_pages = (len(patients_df) - 1) // patients_per_page + 1

        if patients_df.empty:
            st.info("Brak pacjentów.")
        else:
            page = st.number_input("Strona", min_value=1, max_value=total_pages, step=1, value=1)
            start_idx = (page - 1) * patients_per_page
            end_idx = start_idx + patients_per_page

            for _, row in patients_df.iloc[start_idx:end_idx].iterrows():
                render_patient_card(row)


def render_patient_card(row):
    delete_trigger = f"delete_trigger_{row['id']}"
    confirm_trigger = f"confirm_delete_{row['id']}"
    expanded = st.session_state.get(confirm_trigger, False)

    with st.expander(f"SSN: {row['ssn']} - {row['last']} {row['first']}", expanded=expanded):
        if expanded:
            render_delete_confirmation(row)
        else:
            if st.button("Usuń pacjenta", key=delete_trigger):
                st.session_state[confirm_trigger] = True
                st.rerun()

            render_patient_details(row['id'])


def render_delete_confirmation(row):
    st.warning(f"Czy na pewno chcesz usunąć pacjenta **{row['first']} {row['last']}**?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Tak, usuń", key=f"yes_{row['id']}"):
            delete_patient(row['id'], row['first'], row['last'])
    with col2:
        if st.button("Anuluj", key=f"no_{row['id']}"):
            st.session_state[f"confirm_delete_{row['id']}"] = False
            st.rerun()


def delete_patient(patient_id, first, last):
    try:
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_patient(%s)", [patient_id])
        st.success(f"Pacjent {first} {last} został usunięty.")
    except Exception as e:
        st.error(f"Nie udało się usunąć pacjenta: {e}")


def render_patient_details(patient_id):
    details = query_db(f"SELECT * FROM get_patient_details('{patient_id}')")
    st.write("**Numer SSN:**", details.at[0, "ssn"])
    st.write("**Data urodzenia:**", details.at[0, "birthdate"])
    st.write("**Płeć:**", details.at[0, "gender"])
    st.write("**Rasa:**", details.at[0, "race"])
    st.write("**Etniczność:**", details.at[0, "ethnicity"])
    st.write("**Lokalizacja:**", f"{details.at[0, 'lat']}, {details.at[0, 'lon']}")

    render_patient_diagnoses(patient_id)
    render_patient_medications(patient_id)
    render_patient_encounters(patient_id)


def render_patient_diagnoses(patient_id):
    diagnoses = query_db(f"SELECT * FROM get_patient_diagnoses('{patient_id}')")
    if not diagnoses.empty:
        st.write("**Diagnozy:**")
        for desc in diagnoses['description']:
            st.write(f"- {desc}")
    else:
        st.write("**Diagnozy:** brak.")


def render_patient_medications(patient_id):
    medications = query_db(f"SELECT * FROM get_patient_medications('{patient_id}')")
    if not medications.empty:
        st.write("**Przypisane leki:**")
        for _, med in medications.iterrows():
            start = med['start'].strftime("%Y-%m-%d")
            stop = med['stop'].strftime("%Y-%m-%d") if pd.notna(med['stop']) else "..."
            st.write(f"- {med['description']} (od {start} do {stop} - {med['dispenses']} szt.)")
    else:
        st.write("**Przypisane leki:** brak.")


def render_patient_encounters(patient_id):
    encounters = query_db(f"SELECT * FROM get_patient_encounters('{patient_id}')")
    if not encounters.empty:
        st.write("**Pobyty w szpitalu:**")
        for _, enc in encounters.iterrows():
            start_str = enc['start'].strftime("%Y-%m-%d %H:%M")
            stop_str = enc['stop'].strftime("%Y-%m-%d %H:%M")
            st.write(
                f"- {enc['description']} ({enc['encounterclass']}) od {start_str} do {stop_str} "
                f"— koszt: {enc['total_claim_cost']} USD"
            )
    else:
        st.write("**Pobyty w szpitalu:** brak.")



# # ===========================================================
# #                         PACJENCI
# # ===========================================================
# st.header("PACJENCI")
# # -----------------------------------------------
# #                Dodawanie pacjentów
# # -----------------------------------------------

# if "show_add_patient" not in st.session_state:
#     st.session_state.show_add_patient = False


# def toggle_add_patient():
#     st.session_state.show_add_patient = not st.session_state.show_add_patient


# st.button("Dodaj pacjenta", on_click=toggle_add_patient)

# if st.session_state.show_add_patient:
#     with st.form("add_patient"):
#         first_name = st.text_input("Imię", max_chars=30)
#         last_name = st.text_input("Nazwisko", max_chars=30)
#         gender_options = {"Kobieta": "F", "Mężczyzna": "M"}
#         gender_display = st.selectbox("Płeć", options=list(gender_options.keys()))
#         gender = gender_options[gender_display]
#         race = st.text_input("Rasa", max_chars=10)
#         ethnicity = st.text_input("Etniczność", max_chars=20)
#         birthdate = st.date_input(
#             "Data urodzenia",
#             min_value=datetime.date(1900, 1, 1),
#             max_value=datetime.date.today()
#         )
#         ssn = st.text_input("Numer SSN", max_chars=11)
#         lat = st.number_input("Szerokość geograficzna", format="%.6f", step=0.000001)
#         lon = st.number_input("Długość geograficzna", format="%.6f", step=0.000001)
#         submitted = st.form_submit_button("Dodaj pacjenta")

#         if submitted:
#             if not all([first_name, last_name, race, ethnicity, ssn]):
#                 st.warning("Proszę uzupełnić wszystkie dane pacjenta!")
#             else:
#                 try:
#                     conn = psycopg2.connect(**DB_PARAMS)
#                     cur = conn.cursor()
#                     cur.execute("""
#                         CALL add_patient(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#                     """, [
#                         str(uuid.uuid4()), birthdate, ssn, first_name, last_name,
#                         gender, race, ethnicity,
#                         lat if lat != 0 else None,
#                         lon if lon != 0 else None
#                     ])
#                     conn.commit()
#                     cur.close()
#                     conn.close()
#                     st.success("Pacjent został dodany.")
#                     st.session_state.show_add_patient = False
#                 except Exception as e:
#                     st.error(f"Wystąpił błąd!\n{e}")


# # ===========================================================
# #                         ZAPASY
# # ===========================================================
# st.header("MAGAZYN SZPITALA")

# # -----------------------------------------------
# #              Wyświetlanie leków
# # -----------------------------------------------

# if "show_medications" not in st.session_state:
#     st.session_state.show_medications = False


# def toggle_medications():
#     st.session_state.show_medications = not st.session_state.show_medications


# if st.button("Wyświetl zapasy leków", on_click=toggle_medications):
#     pass

# if st.session_state.show_medications:
#     st.subheader("Dostępne leki")

#     medications_summary = query_db("SELECT * FROM get_medications_summary()")

#     if medications_summary.empty:
#         st.info("Brak danych.")
#     else:
#         meds_display = medications_summary.rename(columns={
#             "description": "Nazwa leku",
#             "total_dispenses": "Łączna liczba dawek",
#         })
#         st.dataframe(meds_display, use_container_width=True)

# # -----------------------------------------------
# #              Wyświetlanie zapasów
# # -----------------------------------------------
# if "show_supplies" not in st.session_state:
#     st.session_state.show_supplies = False


# def toggle_supplies():
#     st.session_state.show_supplies = not st.session_state.show_supplies


# if st.button("Wyświetl materiały medyczne", on_click=toggle_supplies):
#     pass

# if st.session_state.show_supplies:
#     st.header("Dostępne materiały medyczne")

#     supplies_summary = query_db("SELECT * FROM get_supplies_summary()")

#     if supplies_summary.empty:
#         st.info("Brak danych.")
#     else:
#         supplies_display = supplies_summary.rename(columns={
#             "description": "Nazwa materiału",
#             "total_quantity": "Łączna liczba"
#         })
#         st.dataframe(supplies_display, use_container_width=True)


# =============================
#        MAIN
# =============================

def main():
    render_statistics()
    render_patient_list()


if __name__ == "__main__":
    main()

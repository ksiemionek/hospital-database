import pytest
import psycopg2
import uuid
from datetime import date


@pytest.fixture(scope="module")
def db_conn():
    conn = psycopg2.connect(
        dbname="szpital_z07",
        user="admin",
        password="password",
        host="localhost",
        port=5432,
    )
    yield conn
    conn.close()


def random_uuid():
    return str(uuid.uuid4())


def test_add_and_delete_patient(db_conn):
    db_conn.rollback()
    patient_id = random_uuid()
    with db_conn.cursor() as cur:
        cur.execute(
            "CALL add_patient(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [
                patient_id,
                date(2000, 1, 1),
                "123-45-6789",
                "John",
                "Doe",
                "M",
                "White",
                "Not Hispanic",
                50.0,
                20.0,
            ],
        )
        db_conn.commit()
        cur.execute("SELECT COUNT(*) FROM patients WHERE id = %s", (patient_id,))
        (count,) = cur.fetchone()
        assert count == 1
        cur.execute("CALL delete_patient(%s)", [patient_id])
        db_conn.commit()
        cur.execute("SELECT COUNT(*) FROM patients WHERE id = %s", (patient_id,))
        (count,) = cur.fetchone()
        assert count == 0


def test_get_gender_distribution(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_gender_distribution()")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_race_distribution(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_race_distribution()")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_patient_locations(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_patient_locations()")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_top_diagnoses(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_top_diagnoses(5)")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_search_patients(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM search_patients('John')")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_all_patients(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_all_patients()")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_patient_details(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        patient_id = random_uuid()
        cur.execute(
            "CALL add_patient(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            [
                patient_id,
                date(2000, 1, 1),
                "987-65-4321",
                "Alice",
                "Smith",
                "F",
                "Black",
                "Hispanic",
                40.0,
                30.0,
            ],
        )
        db_conn.commit()
        cur.execute("SELECT * FROM get_patient_details(%s)", (patient_id,))
        row = cur.fetchone()
        assert row is not None
        cur.execute("CALL delete_patient(%s)", [patient_id])
        db_conn.commit()


def test_get_patient_diagnoses(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_patient_diagnoses(NULL)")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_patient_medications(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_patient_medications(NULL)")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_patient_encounters(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_patient_encounters(NULL)")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_medications_summary(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_medications_summary()")
        rows = cur.fetchall()
        assert isinstance(rows, list)


def test_get_supplies_summary(db_conn):
    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT * FROM get_supplies_summary()")
        rows = cur.fetchall()
        assert isinstance(rows, list)

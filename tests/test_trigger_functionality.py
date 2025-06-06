import pytest
import psycopg2
import uuid
from datetime import datetime, timedelta


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


def test_patients_delete_audit_trigger(db_conn):
    patient_id = random_uuid()
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO patients (id, birthdate, ssn, first, last, race, ethnicity, gender)
            VALUES (%s, '2000-01-01', %s, 'John', 'Doe', 'White', 'Not Hispanic', 'M')
        """,
            (patient_id, patient_id[:11]),
        )
        db_conn.commit()
        cur.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
        db_conn.commit()
        cur.execute(
            "SELECT COUNT(*) FROM patients_audit WHERE patientid = %s AND operation = 'DELETE'",
            (patient_id,),
        )
        (count,) = cur.fetchone()
        assert count == 1


def test_patients_audit_cleanup_trigger(db_conn):
    with db_conn.cursor() as cur:
        for i in range(101):
            cur.execute(
                """
                INSERT INTO patients_audit(patientid, operation, deletedat, data)
                VALUES (%s, 'DELETE', CURRENT_TIMESTAMP, '{}'::jsonb)
            """,
                (random_uuid(),),
            )
        db_conn.commit()
        cur.execute("SELECT COUNT(*) FROM patients_audit")
        (count,) = cur.fetchone()
        assert count == 100


def test_prevent_duplicate_immunization_trigger(db_conn):
    patient_id = random_uuid()
    encounter_id = random_uuid()
    org_id = random_uuid()
    provider_id = random_uuid()
    payer_id = random_uuid()
    code = "IMM1"
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO organizations (id, name, address, city, state, zip, lat, lon, revenue, utilization)
            VALUES (%s, 'Org', 'Addr', 'City', 'ST', '12345', 0, 0, 1, 1)
            """,
            (org_id,),
        )
        cur.execute(
            """
            INSERT INTO providers (id, organization, name, gender, speciality, address, city, state, zip, lat, lon, utilization)
            VALUES (%s, %s, 'Prov', 'M', 'Spec', 'Addr', 'City', 'ST', '12345', 0, 0, 1)
            """,
            (provider_id, org_id),
        )
        cur.execute(
            """
            INSERT INTO payers (id, name)
            VALUES (%s, 'Payer')
            """,
            (payer_id,),
        )
        cur.execute(
            """
            INSERT INTO patients (id, birthdate, ssn, first, last, race, ethnicity, gender)
            VALUES (%s, '2000-01-01', %s, 'Jane', 'Smith', 'White', 'Not Hispanic', 'F')
            """,
            (patient_id, patient_id[:11]),
        )
        cur.execute(
            """
            INSERT INTO encounters (id, start, stop, patient, organization, provider, payer, encounterclass, code, description, base_encounter_cost, total_claim_cost, payer_coverage)
            VALUES (%s, now(), now(), %s, %s, %s, %s, 'class', 'code', 'desc', 1, 1, 1)
            """,
            (encounter_id, patient_id, org_id, provider_id, payer_id),
        )
        db_conn.commit()
        cur.execute(
            """
            INSERT INTO immunizations (date, patient, encounter, code, description, base_cost)
            VALUES (now(), %s, %s, %s, 'desc', 1)
            """,
            (patient_id, encounter_id, code),
        )
        db_conn.commit()
        with pytest.raises(psycopg2.errors.RaiseException):
            cur.execute(
                """
                INSERT INTO immunizations (date, patient, encounter, code, description, base_cost)
                VALUES (now(), %s, %s, %s, 'desc', 1)
                """,
                (patient_id, encounter_id, code),
            )
        db_conn.rollback()


def test_prevent_med_after_death_trigger(db_conn):
    db_conn.rollback()
    patient_id = random_uuid()
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO patients (id, birthdate, deathdate, ssn, first, last, race, ethnicity, gender)
            VALUES (%s, '2000-01-01', %s, %s, 'Dead', 'Patient', 'White', 'Not Hispanic', 'M')
        """,
            (patient_id, datetime.now().date(), patient_id[:11]),
        )
        db_conn.commit()
        with pytest.raises(psycopg2.errors.RaiseException):
            cur.execute(
                """
                INSERT INTO medications (start, stop, patient, payer, encounter, code, description, base_cost, payer_coverage, dispenses, totalcost)
                VALUES (now(), now(), %s, %s, %s, 'MED1', 'desc', 1, 1, 1, 1)
            """,
                (patient_id, random_uuid(), random_uuid()),
            )
        db_conn.rollback()


def test_validate_encounter_dates_trigger(db_conn):
    patient_id = random_uuid()
    org_id = random_uuid()
    provider_id = random_uuid()
    payer_id = random_uuid()
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO patients (id, birthdate, ssn, first, last, race, ethnicity, gender)
            VALUES (%s, '2000-01-01', %s, 'Test', 'User', 'White', 'Not Hispanic', 'M')
        """,
            (patient_id, patient_id[:11]),
        )
        cur.execute(
            """
            INSERT INTO organizations (id, name, address, city, state, zip, lat, lon, revenue, utilization)
            VALUES (%s, 'Org', 'Addr', 'City', 'ST', '12345', 0, 0, 1, 1)
        """,
            (org_id,),
        )
        cur.execute(
            """
            INSERT INTO providers (id, organization, name, gender, speciality, address, city, state, zip, lat, lon, utilization)
            VALUES (%s, %s, 'Prov', 'M', 'Spec', 'Addr', 'City', 'ST', '12345', 0, 0, 1)
        """,
            (provider_id, org_id),
        )
        cur.execute(
            """
            INSERT INTO payers (id, name) VALUES (%s, 'Payer')
        """,
            (payer_id,),
        )
        db_conn.commit()
        with pytest.raises(psycopg2.errors.RaiseException):
            cur.execute(
                """
                INSERT INTO encounters (id, start, stop, patient, organization, provider, payer, encounterclass, code, description, base_encounter_cost, total_claim_cost, payer_coverage)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'class', 'code', 'desc', 1, 1, 1)
            """,
                (
                    random_uuid(),
                    datetime.now(),
                    datetime.now() - timedelta(days=1),
                    patient_id,
                    org_id,
                    provider_id,
                    payer_id,
                ),
            )
        db_conn.rollback()


def test_validate_observation_trigger(db_conn):
    patient_id = random_uuid()
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO patients (id, birthdate, ssn, first, last, race, ethnicity, gender)
            VALUES (%s, '2000-01-01', %s, 'Obs', 'Test', 'White', 'Not Hispanic', 'M')
        """,
            (patient_id, patient_id[:11]),
        )
        db_conn.commit()
        with pytest.raises(psycopg2.errors.RaiseException):
            cur.execute(
                """
                INSERT INTO observations (date, patient, code, description, value, units, type)
                VALUES (%s, %s, 'CODE', 'desc', '1', 'unit', 'type')
            """,
                (datetime.now() + timedelta(days=1), patient_id),
            )
        db_conn.rollback()


def test_update_claim_total_trigger(db_conn):
    claim_id = random_uuid()
    patient_id = random_uuid()
    provider_id = random_uuid()
    org_id = random_uuid()
    payer_id = random_uuid()
    encounter_id = random_uuid()
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO organizations (id, name, address, city, state, zip, lat, lon, revenue, utilization)
            VALUES (%s, 'Org', 'Addr', 'City', 'ST', '12345', 0, 0, 1, 1)
            """,
            (org_id,),
        )
        cur.execute(
            """
            INSERT INTO payers (id, name)
            VALUES (%s, 'Payer')
            """,
            (payer_id,),
        )
        cur.execute(
            """
            INSERT INTO patients (id, birthdate, ssn, first, last, race, ethnicity, gender)
            VALUES (%s, '2000-01-01', %s, 'Claim', 'Test', 'White', 'Not Hispanic', 'M')
            """,
            (patient_id, patient_id[:11]),
        )
        cur.execute(
            """
            INSERT INTO providers (id, organization, name, gender, speciality, address, city, state, zip, lat, lon, utilization)
            VALUES (%s, %s, 'Prov', 'M', 'Spec', 'Addr', 'City', 'ST', '12345', 0, 0, 1)
            """,
            (provider_id, org_id),
        )
        cur.execute(
            """
            INSERT INTO encounters (id, start, stop, patient, organization, provider, payer, encounterclass, code, description, base_encounter_cost, total_claim_cost, payer_coverage)
            VALUES (%s, now(), now(), %s, %s, %s, %s, 'class', 'code', 'desc', 1, 1, 1)
            """,
            (encounter_id, patient_id, org_id, provider_id, payer_id),
        )
        cur.execute(
            """
            INSERT INTO claims (id, patientid, providerid, departmentid, patientdepartmentid, appointmentid)
            VALUES (%s, %s, %s, 1, 1, %s)
            """,
            (claim_id, patient_id, provider_id, encounter_id),
        )
        db_conn.commit()
        cur.execute(
            """
            INSERT INTO claims_transactions (id, claimid, chargeid, patientid, type, fromdate, todate, placeofservice, amount, providerid, supervisingproviderid)
            VALUES (%s, %s, 1, %s, 'type', now(), now(), %s, 100, %s, %s)
            """,
            (
                random_uuid(),
                claim_id,
                patient_id,
                org_id,
                provider_id,
                provider_id,
            ),
        )
        db_conn.commit()
        cur.execute("SELECT totalamount FROM claims WHERE id = %s", (claim_id,))
        (total,) = cur.fetchone()
        assert total == 100

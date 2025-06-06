import pytest
import psycopg2

EXPECTED_TABLES = [
    "patients",
    "payers",
    "organizations",
    "payer_transitions",
    "procedures",
    "providers",
    "supplies",
    "encounters",
    "imaging_studies",
    "immunizations",
    "medications",
    "observations",
    "allergies",
    "careplans",
    "claims_transactions",
    "claims",
    "conditions",
    "devices",
    "patients_audit",
]

EXPECTED_CONSTRAINTS = [
    ("patients", "patients_pkey"),
    ("patients", "unique_ssn"),
    ("payers", "payers_pkey"),
    ("organizations", "organizations_pkey"),
    ("providers", "providers_pkey"),
    ("supplies", "fk_patient"),
    ("supplies", "fk_encounter"),
    ("encounters", "encounters_pkey"),
    ("encounters", "fk_patient"),
    ("imaging_studies", "imaging_studies_pkey"),
    ("immunizations", "fk_patient"),
    ("medications", "fk_patient"),
    ("allergies", "fk_patient"),
    ("careplans", "careplans_pkey"),
    ("claims_transactions", "claims_transactions_pkey"),
]

EXPECTED_VIEWS = [
    "medication_summary",
    "supply_summary",
]

EXPECTED_INDEXES = [
    "idx_patients_id",
    "idx_patients_ssn",
    "idx_patients_last",
    "idx_patients_first",
    "idx_patients_lat_lon",
    "idx_patients_gender",
    "idx_patients_race",
    "idx_medications_patient_start",
    "idx_conditions_patient_desc_start",
    "idx_conditions_description",
    "idx_encounters_patient_start",
    "idx_payer_transitions_patient",
    "idx_payer_transitions_payer",
    "idx_encounters_payer",
    "idx_procedures_encounter",
    "idx_medications_payer",
]


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


@pytest.mark.parametrize("table", EXPECTED_TABLES)
def test_table_exists(db_conn, table):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = %s
            );
            """,
            (table,),
        )
        (exists,) = cur.fetchone()
        assert exists, f"Table '{table}' does not exist"


@pytest.mark.parametrize("table,constraint", EXPECTED_CONSTRAINTS)
def test_constraint_exists(db_conn, table, constraint):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE table_name = %s AND constraint_name = %s
            );
            """,
            (table, constraint),
        )
        (exists,) = cur.fetchone()
        assert exists, f"Constraint '{constraint}' on table '{table}' does not exist"


@pytest.mark.parametrize("view", EXPECTED_VIEWS)
def test_view_exists(db_conn, view):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.views
                WHERE table_name = %s
            );
            """,
            (view,),
        )
        (exists,) = cur.fetchone()
        assert exists, f"View '{view}' does not exist"


@pytest.mark.parametrize("index", EXPECTED_INDEXES)
def test_index_exists(db_conn, index):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = %s
            );
            """,
            (index,),
        )
        (exists,) = cur.fetchone()
        assert exists, f"Index '{index}' does not exist"

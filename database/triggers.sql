DROP TRIGGER IF EXISTS trg_patients_after_delete ON patients;
DROP TRIGGER IF EXISTS trg_patients_audit_after_insert ON patients_audit;
DROP TRIGGER IF EXISTS trg_update_claim_total ON claims_transactions;
DROP TRIGGER IF EXISTS trg_prevent_med_after_death ON medications;
DROP TRIGGER IF EXISTS trg_visit_after_insert ON encounters;
DROP TRIGGER IF EXISTS trg_claim_before_insert ON claims;
DROP TRIGGER IF EXISTS trg_validate_observation ON observations;
DROP TRIGGER IF EXISTS trg_prevent_duplicate_immunization ON immunizations;
DROP TRIGGER IF EXISTS trg_validate_encounter_dates ON encounters;
DROP TRIGGER IF EXISTS trg_increment_patient_procedure_count ON procedures;

-- Saves deleted row from patiants to patients_audit as JSONB
CREATE OR REPLACE FUNCTION patients_delete_audit_fn() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO patients_audit(patientid, operation, deletedat, data)
    VALUES (
        OLD.id,
        'DELETE',
        CURRENT_TIMESTAMP,
        to_jsonb(OLD)
    );
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patients_after_delete
AFTER DELETE ON patients
FOR EACH ROW
EXECUTE FUNCTION patients_delete_audit_fn();


-- Deletes the oldest row from patient_audit after insert if number of rows reaches 100
CREATE OR REPLACE FUNCTION patients_audit_cleanup_fn() RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM patients_audit) > 100 THEN
        DELETE FROM patients_audit
        WHERE ctid IN (
            SELECT ctid FROM patients_audit
            ORDER BY deletedat ASC
            LIMIT 1
        );
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_patients_audit_after_insert
AFTER INSERT ON patients_audit
FOR EACH ROW
EXECUTE FUNCTION patients_audit_cleanup_fn();


-- Calculates total cost for a claim after any changes in claims_transactions
CREATE OR REPLACE FUNCTION update_claim_total()
RETURNS TRIGGER AS $$
DECLARE
    claim_id_old UUID;
    claim_id_new UUID;
    new_total NUMERIC(12,2);
BEGIN
    IF (TG_OP = 'DELETE') THEN
        claim_id_old := OLD.CLAIMID;
    ELSIF (TG_OP = 'UPDATE') THEN
        claim_id_old := OLD.CLAIMID;
        claim_id_new := NEW.CLAIMID;
    ELSIF (TG_OP = 'INSERT') THEN
        claim_id_new := NEW.CLAIMID;
    END IF;

    IF claim_id_old IS NOT NULL AND claim_id_new IS NOT NULL AND claim_id_old <> claim_id_new THEN
        SELECT COALESCE(SUM(AMOUNT), 0) INTO new_total
        FROM claims_transactions
        WHERE CLAIMID = claim_id_old;
        UPDATE claims SET totalamount = new_total WHERE id = claim_id_old;

        SELECT COALESCE(SUM(AMOUNT), 0) INTO new_total
        FROM claims_transactions
        WHERE CLAIMID = claim_id_new;
        UPDATE claims SET totalamount = new_total WHERE id = claim_id_new;

    ELSE
        IF claim_id_new IS NOT NULL THEN
            SELECT COALESCE(SUM(AMOUNT), 0) INTO new_total
            FROM claims_transactions
            WHERE CLAIMID = claim_id_new;
            UPDATE claims SET totalamount = new_total WHERE id = claim_id_new;

        ELSIF claim_id_old IS NOT NULL THEN
            SELECT COALESCE(SUM(AMOUNT), 0) INTO new_total
            FROM claims_transactions
            WHERE CLAIMID = claim_id_old;
            UPDATE claims SET totalamount = new_total WHERE id = claim_id_old;
        END IF;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_claim_total
AFTER INSERT OR UPDATE OR DELETE ON claims_transactions
FOR EACH ROW
EXECUTE FUNCTION update_claim_total();


-- Forbids changing medications for a dead patient
CREATE OR REPLACE FUNCTION prevent_med_after_death()
RETURNS TRIGGER AS $$
DECLARE
    death_date DATE;
BEGIN
    SELECT DEATHDATE INTO death_date
    FROM PATIENTS
    WHERE ID = NEW.PATIENT;

    IF death_date IS NOT NULL AND death_date <= CURRENT_DATE THEN
        RAISE EXCEPTION 'Cannot asign medication to a dead patient (ID=%, date of death=%).', NEW.PATIENT, death_date;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_med_after_death
BEFORE INSERT OR UPDATE ON MEDICATIONS
FOR EACH ROW
EXECUTE FUNCTION prevent_med_after_death();


-- Updates last visit date in PATIENTS after new visit
CREATE OR REPLACE FUNCTION update_patient_last_visit() RETURNS TRIGGER AS $$
DECLARE
    current_last TIMESTAMP;
BEGIN
    SELECT LASTVISIT INTO current_last FROM PATIENT WHERE PATIENTID = NEW.PATIENTID;
    IF NEW.START IS NOT NULL AND (current_last IS NULL OR NEW.START > current_last) THEN
        UPDATE PATIENT SET LASTVISIT = NEW.START WHERE PATIENTID = NEW.PATIENTID;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TRG_VISIT_AFTER_INSERT
AFTER INSERT ON ENCOUNTERS
FOR EACH ROW
EXECUTE FUNCTION update_patient_last_visit();


-- Sets create date for new claims
CREATE OR REPLACE FUNCTION set_claim_defaults() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CREATEDAT IS NULL THEN
        NEW.CREATEDAT := CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER TRG_CLAIM_BEFORE_INSERT
BEFORE INSERT ON CLAIMS
FOR EACH ROW
EXECUTE FUNCTION set_claim_defaults();


-- Validates date and value in observation
CREATE OR REPLACE FUNCTION validate_observation()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.effectivedate > NOW() THEN
        RAISE EXCEPTION 'Measurement date (%) cannot be in the future.', NEW.effectivedate;
    END IF;

    IF NEW.numericvalue < 0 THEN
        RAISE EXCEPTION 'The measurement value (%) cannot be negative.', NEW.numericvalue;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_observation
BEFORE INSERT OR UPDATE ON observations
FOR EACH ROW EXECUTE FUNCTION validate_observation();


-- Blocks repeated registration of the same vaccine on a given day for a given patient
CREATE OR REPLACE FUNCTION prevent_duplicate_immunization()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM immunizations
        WHERE patient = NEW.patient
          AND code = NEW.code
          AND DATE(date) = DATE(NEW.date)
    ) THEN
        RAISE EXCEPTION 'The patient (ID=%) has already received the immunization with code % on the same day (%).',
            NEW.patient, NEW.code, NEW.date;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_prevent_duplicate_immunization
BEFORE INSERT ON immunizations
FOR EACH ROW
EXECUTE FUNCTION prevent_duplicate_immunization();


-- Checks if start date is earlier than end date in encounters, otherwise raises exception
CREATE OR REPLACE FUNCTION validate_encounter_dates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.start IS NOT NULL
       AND NEW.end IS NOT NULL
       AND NEW.end < NEW.start THEN
        RAISE EXCEPTION 'End date (%s) cannot be earlier than start date (%s).',
                        NEW.end, NEW.start;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_encounter_dates
BEFORE INSERT OR UPDATE ON encounters
FOR EACH ROW
EXECUTE FUNCTION validate_encounter_dates();


-- Increments procedure count for patient after new procedure
CREATE OR REPLACE FUNCTION increment_patient_procedure_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE patients
    SET procedurecount = COALESCE(procedurecount, 0) + 1
    WHERE id = NEW.patient;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_increment_patient_procedure_count
AFTER INSERT ON procedures
FOR EACH ROW
EXECUTE FUNCTION increment_patient_procedure_count();

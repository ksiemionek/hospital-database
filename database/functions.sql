CREATE OR REPLACE PROCEDURE add_patient(
    IN p_id UUID,
    IN p_birthdate DATE,
    IN p_ssn VARCHAR,
    IN p_first VARCHAR,
    IN p_last VARCHAR,
    IN p_gender CHAR(1),
    IN p_race VARCHAR,
    IN p_ethnicity VARCHAR,
    IN p_lat NUMERIC(11,8),
    IN p_lon NUMERIC(11,8)
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF p_gender NOT IN ('M', 'F') THEN
        RAISE EXCEPTION 'Invalid gender: % (expected "M" or "F")', p_gender;
    END IF;

    IF p_birthdate > CURRENT_DATE THEN
        RAISE EXCEPTION 'Birthdate cannot be in the future: %', p_birthdate;
    END IF;

    IF p_lat IS NOT NULL AND (p_lat < -90 OR p_lat > 90) THEN
        RAISE EXCEPTION 'Invalid latitude: % (must be between -90 and 90)', p_lat;
    END IF;

    IF p_lon IS NOT NULL AND (p_lon < -180 OR p_lon > 180) THEN
        RAISE EXCEPTION 'Invalid longitude: % (must be between -180 and 180)', p_lon;
    END IF;

    INSERT INTO patients (
        id, birthdate, ssn, first, last,
        gender, race, ethnicity, lat, lon
    ) VALUES (
        p_id, p_birthdate, p_ssn, p_first, p_last,
        p_gender, p_race, p_ethnicity, p_lat, p_lon
    );
END;
$$;


CREATE OR REPLACE PROCEDURE delete_patient(p_patient_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM patients WHERE id = p_patient_id;
END;
$$;


CREATE OR REPLACE FUNCTION get_gender_distribution()
RETURNS TABLE (gender TEXT, count BIGINT)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.gender::TEXT, COUNT(*)::BIGINT
    FROM patients p
    GROUP BY p.gender;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_race_distribution()
RETURNS TABLE (race TEXT, count BIGINT)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.race::TEXT, COUNT(*)::BIGINT
    FROM patients p
    GROUP BY p.race;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_patient_locations()
RETURNS TABLE (lat DOUBLE PRECISION, lon DOUBLE PRECISION)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.lat::DOUBLE PRECISION, p.lon::DOUBLE PRECISION
    FROM patients p
    WHERE p.lat IS NOT NULL AND p.lon IS NOT NULL;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_top_diagnoses(limit_count INT DEFAULT 20)
RETURNS TABLE (description TEXT, count BIGINT)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.description::TEXT, COUNT(*)::BIGINT
    FROM conditions c
    WHERE c.description LIKE '%(disorder)'
    GROUP BY c.description
    ORDER BY COUNT(*) DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION search_patients(term TEXT)
RETURNS TABLE (id UUID, ssn TEXT, last TEXT, first TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.ssn::TEXT, p.last::TEXT, p.first::TEXT
    FROM patients p
    WHERE p.ssn ILIKE '%' || term || '%'
       OR p.last ILIKE '%' || term || '%'
       OR p.first ILIKE '%' || term || '%'
    ORDER BY p.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_all_patients()
RETURNS TABLE (id UUID, ssn TEXT, last TEXT, first TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.ssn::TEXT, p.last::TEXT, p.first::TEXT
    FROM patients p
    ORDER BY p.id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_patient_details(patient_id UUID)
RETURNS TABLE (
    birthdate DATE,
    gender TEXT,
    race TEXT,
    ethnicity TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    ssn TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT p.birthdate, p.gender::TEXT, p.race::TEXT, p.ethnicity::TEXT,
           p.lat::DOUBLE PRECISION, p.lon::DOUBLE PRECISION, p.ssn::TEXT
    FROM patients p
    WHERE p.id = patient_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_patient_diagnoses(patient_id UUID)
RETURNS TABLE (description TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.description::TEXT
    FROM conditions c
    WHERE c.patient = patient_id AND c.description LIKE '%(disorder)'
    ORDER BY c.start DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_patient_medications(patient_id UUID)
RETURNS TABLE (
    description TEXT,
    start TIMESTAMP,
    stop TIMESTAMP,
    dispenses INTEGER
)
AS $$
BEGIN
    RETURN QUERY
    SELECT m.description::TEXT, m.start, m.stop, m.dispenses
    FROM medications m
    WHERE m.patient = patient_id
    ORDER BY m.start DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_patient_encounters(patient_id UUID)
RETURNS TABLE (
    start TIMESTAMP,
    stop TIMESTAMP,
    encounterclass TEXT,
    description TEXT,
    total_claim_cost NUMERIC
)
AS $$
BEGIN
    RETURN QUERY
    SELECT e.start, e.stop, e.encounterclass::TEXT, e.description::TEXT, e.total_claim_cost
    FROM encounters e
    WHERE e.patient = patient_id
    ORDER BY e.start DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_medications_summary()
RETURNS TABLE (
    description TEXT,
    total_dispenses BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT ms.description::TEXT, ms.total_dispenses::BIGINT
    FROM medication_summary ms
    ORDER BY ms.total_dispenses DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_supplies_summary()
RETURNS TABLE (
    description TEXT,
    total_quantity BIGINT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT ss.description::TEXT, ss.total_quantity::BIGINT
    FROM supply_summary ss
    ORDER BY ss.total_quantity DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql;

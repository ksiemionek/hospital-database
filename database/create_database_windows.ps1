# download data.zip manually
Expand-Archive -Path "data.zip" -DestinationPath "."

# CREATE DATABASE
docker cp ./database/create_schema.sql postgres:/tmp/create_schema.sql
docker exec -i postgres psql -U admin -d szpital_z07 -f /tmp/create_schema.sql

# PATIENTS
docker cp ./csv/patients.csv postgres:/tmp/patients.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY PATIENTS FROM '/tmp/patients.csv' DELIMITER ',' CSV HEADER;"

# ORGANIZATIONS
docker cp ./csv/organizations.csv postgres:/tmp/organizations.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY ORGANIZATIONS FROM '/tmp/organizations.csv' DELIMITER ',' CSV HEADER;"

# PAYERS
docker cp ./csv/payers.csv postgres:/tmp/payers.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY PAYERS FROM '/tmp/payers.csv' DELIMITER ',' CSV HEADER;"

# PROVIDERS
docker cp ./csv/providers.csv postgres:/tmp/providers.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY PROVIDERS FROM '/tmp/providers.csv' DELIMITER ',' CSV HEADER;"

# ENCOUNTERS
docker cp ./csv/encounters.csv postgres:/tmp/encounters.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY ENCOUNTERS FROM '/tmp/encounters.csv' DELIMITER ',' CSV HEADER;"

# PAYER_TRANSITIONS
docker cp ./csv/payer_transitions.csv postgres:/tmp/payer_transitions.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY PAYER_TRANSITIONS FROM '/tmp/payer_transitions.csv' DELIMITER ',' CSV HEADER;"

# PROCEDURES
docker cp ./csv/procedures.csv postgres:/tmp/procedures.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY PROCEDURES FROM '/tmp/procedures.csv' DELIMITER ',' CSV HEADER;"

# SUPPLIES
docker cp ./csv/supplies.csv postgres:/tmp/supplies.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY SUPPLIES FROM '/tmp/supplies.csv' DELIMITER ',' CSV HEADER;"

# IMAGING_STUDIES
docker cp ./csv/imaging_studies.csv postgres:/tmp/imaging_studies.csv
docker cp ./database/fix_imaging_studies.sql postgres:/tmp/fix_imaging_studies.sql
docker exec -i postgres psql -U admin -d szpital_z07 -f /tmp/fix_imaging_studies.sql

# IMMUNIZATIONS
docker cp ./csv/immunizations.csv postgres:/tmp/immunizations.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY IMMUNIZATIONS FROM '/tmp/immunizations.csv' DELIMITER ',' CSV HEADER;"

# MEDICATIONS
docker cp ./csv/medications.csv postgres:/tmp/medications.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY MEDICATIONS FROM '/tmp/medications.csv' DELIMITER ',' CSV HEADER;"

# OBSERVATIONS
docker cp ./csv/observations.csv postgres:/tmp/observations.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY OBSERVATIONS FROM '/tmp/observations.csv' DELIMITER ',' CSV HEADER;"

# ALLERGIES
docker cp ./csv/allergies.csv postgres:/tmp/allergies.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY ALLERGIES FROM '/tmp/allergies.csv' DELIMITER ',' CSV HEADER;"

# CAREPLANS
docker cp ./csv/careplans.csv postgres:/tmp/careplans.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY CAREPLANS FROM '/tmp/careplans.csv' DELIMITER ',' CSV HEADER;"

# CLAIMS
docker cp ./csv/claims.csv postgres:/tmp/claims.csv
docker cp ./database/fix_claims.sql postgres:/tmp/fix_claims.sql
docker exec -i postgres psql -U admin -d szpital_z07 -f /tmp/fix_claims.sql

# CLAIMS_TRANSACTIONS
docker cp ./csv/claims_transactions.csv postgres:/tmp/claims_transactions.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY CLAIMS_TRANSACTIONS FROM '/tmp/claims_transactions.csv' DELIMITER ',' CSV HEADER;"

# CONDITIONS
docker cp ./csv/conditions.csv postgres:/tmp/conditions.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY CONDITIONS FROM '/tmp/conditions.csv' DELIMITER ',' CSV HEADER;"

# DEVICES
docker cp ./csv/devices.csv postgres:/tmp/devices.csv
docker exec -i postgres psql -U admin -d szpital_z07 -c "COPY DEVICES FROM '/tmp/devices.csv' DELIMITER ',' CSV HEADER;"

# ALTER PATIENTS
docker cp ./database/alter_patients.sql postgres:/tmp/alter_patients.sql
docker exec -i postgres psql -U admin -d szpital_z07 -f /tmp/alter_patients.sql

# TRIGGERS
docker cp ./database/triggers.sql postgres:/tmp/triggers.sql
docker exec -i postgres psql -U admin -d szpital_z07 -f /tmp/triggers.sql

# FUNCTIONS AND PROCEDURES
docker cp ./database/functions.sql postgres:/tmp/functions.sql
docker exec -i postgres psql -U admin -d szpital_z07 -f /tmp/functions.sql

Remove-Item -Recurse -Force .\csv

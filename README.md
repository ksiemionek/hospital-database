# Bazy Danych 2 - Projekt Szpitala

Grupa: Z07

- Michał Mizia
- Kacper Siemionek
- Michał Pędziwiatr
- Miłosz Andryszczuk
- Wojtek Zieziula

## Odpalenie dockera

```sh
docker compose up -d
```

url=postgresql://admin:password@localhost:5432/szpital_z07
username=admin
password=password

## Zbiór danych

Dane do projektu pochodzą ze strony https://synthea.mitre.org/downloads, konkretnie zbiór `1K Sample Synthetic Patient Records, CSV | [mirror]: 9 MB`

## Utworzenie bazy danych

Po udanym uruchomieniu bazy danych w Dockerze należy uruchomić skrypt `create_database.sh`, który pobiera plik .zip z danymi do wstawienia, a następnie tworzy bazę danych na podstawie pliku `create_schema.sql` i wstawia do niego wszystkie dane.

```sh
chmod +x create_database.sh
./create_database.sh
```

## Uruchomienie aplikacji

Aby uruchomić aplikację, najpierw należy zainstalować potrzebne biblioteki:

```sh
pip install streamlit pandas plotly psycopg2-binary
```

Po udanym zainstalowaniu możemy uruchomić aplikację.

```sh
streamlit run app.py
```

# Dokumentacja

## Cel projektu

Celem naszego projektu było utworzenie bazy danych umożliwiającej zarządzanie danymi medycznymi pacjentów, wizytami, procedurami, rozliceniami, zasobami szpitala itp.

## Podział pracy

- Kacper Siemionek: struktura i połączenia tabel, opytmalizacja za pomocą indeksów, wizualizacja danych w aplikacji webowej, skrypt do utworzenia bazy
- Michał Pędziwiatr: Aplikacja webowa, optymalizacja bazy danych oraz zwizualizowanie jej struktury za pomocą diagramu
- Miłosz Andryszczuk: funkcje, procedury i triggery – walidacja danych, automatyczne aktualizacje oraz audyt operacji usuwania

## Dane techniczne

- Baza danych PostgreSQL
- Aplikacja w języku Python wykorzystująca bibliotekę Streamlit

## Opis tabel

### Tabele podstawowe

- `patients` - dane osobiste pacjentów
- `payers` - informacje o płatnikach
- `encounters` - rejestracje wizyt
- `providers` - dostawcy usług medycznych
- `organizations` - instytucje medyczne

### Tabele kliniczne

- `conditions` - choroby, urazy pacjentów
- `medications` - przepisane leki
- `procedures` - wykonane procedury medyczne
- `immunizations` - szczepienia pacjentów
- `allergies` - alergie pacjentów
- `observations` - obserwacje, wyniki badań
- `imaging_studies` - dokumentacja badań diagnostycznych
- `careplans` - dokumentacja planów i celów leczenia
- `supplies` - zaopatrzenie medyczne
- `devices` - zarejestrowane urzązdzenia

### Tabele finansowe

- `claims` - roszczenia ubezpieczeniowe
- `claims_transactions` - transakcje finansowe dotyczące ubezpieczeń
- `payer_transitions` - historia zmian ubezpieczeń


## Funkcjonalność

Baza danych została zoptymalizowana za pomocą odpowiednich indeksów przyspieszających operowanie na danych. Wprowadziliśmy również niezbędne funkcje i procedury potrzebne do działania aplikacji:

### Procedury

- `add_patient` – dodaje pacjenta do systemu po uprzedniej walidacji danych wejściowych
- `delete_patient` – usuwa pacjenta oraz jego powiązane dane

### Funkcje

- `get_gender_distribution` – zwraca rozkład pacjentów według płci
- `get_race_distribution` – zwraca rozkład pacjentów według rasy
- `get_patient_locations` – zwraca współrzędne geograficzne pacjentów
- `get_top_diagnoses` – zwraca najczęściej występujące diagnozy
- `search_patients` – umożliwia wyszukiwanie pacjentów po imieniu, nazwisku lub numerze SSN
- `get_all_patients` – zwraca wszystkich pacjentów
- `get_patient_details` – zwraca szczegóły pojedynczego pacjenta
- `get_patient_diagnoses` – zwraca ostatnie diagnozy danego pacjenta
- `get_patient_medications` – zwraca ostatnio przepisane leki pacjenta
- `get_patient_encounters` – zwraca ostatnie wizyty danego pacjenta w szpitalu
- `get_medications_summary` – zwraca 20 najczęściej przepisywanych leków
- `get_supplies_summary` – zwraca 20 najczęściej zużywanych materiałów medycznych


### Triggery
Poza funkcjami dostępne są równie wyzwalacze wykorzystywane w bazie danych do walidacji, automatycznych aktualizacji oraz utrzymania integralności danych:

#### Audyt

- `trg_patients_after_delete` – zapisuje usunięte rekordy z `patients` do `patients_audit` jako JSONB
- `trg_patients_audit_after_insert` – ogranicza rozmiar tabeli `patients_audit` do 100 rekordów, usuwając najstarsze wpisy po każdym dodaniu

#### Walidacja danych

- `trg_prevent_duplicate_immunization` – uniemożliwia dodanie tej samej szczepionki dla danego pacjenta tego samego dnia
- `trg_prevent_med_after_death` – zapobiega przypisywaniu leków pacjentowi, który już nie żyje
- `trg_validate_encounter_dates` – wymusza, aby data zakończenia wizyty nie była wcześniejsza niż data rozpoczęcia
- `trg_validate_observation` – sprawdza poprawność danych wstawianych do tabeli `observations`

#### Automatyczne aktualizacje

- `trg_update_claim_total` – przelicza łączną kwotę roszczenia po każdej modyfikacji powiązanych transakcji w `claims_transactions`
- `trg_visit_after_insert` – aktualizuje datę ostatniej wizyty pacjenta po każdej nowej rejestracji w tabeli `encounters`
- `trg_claim_before_insert` – ustawia domyślną datę utworzenia roszczenia, jeśli nie została podana
- `trg_increment_patient_procedure_count` – inkrementuje licznik procedur pacjenta po dodaniu nowej procedury medycznej

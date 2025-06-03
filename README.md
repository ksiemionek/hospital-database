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

- Kacper Siemionek: struktura i połączenia tabel, indeksy, aplikacja webowa, skrypt do utworzenia bazy
- # Michał Pędziwiatr: Aplikacja webowa, optymalizacja bazy danych oraz zwizualizowanie jej struktury za pomocą diagramu

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

- `conditions` - 
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

Baza danych została zoptymalizowana za pomocą odpowiednich indeksów przyspieszających operowanie na danych. Wprowadziliśmy również niezbędne funkcje potrzebne do działania aplikacji:

- tu funkcje i krotki opis jak w tabelach

Poza funkcjami dostępne są równie wyzwalacze konieczne do prawidłowej pracy bazy:

- tu triggery i krotki opis
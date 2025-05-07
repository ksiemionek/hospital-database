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

Po udanym zainstalowaniu mozemy uruchomić aplikację.

```sh
streamlit run app.py
```

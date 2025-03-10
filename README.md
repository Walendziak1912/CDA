# CDA Premium Downloader

Program do pobierania filmów z CDA Premium napisany w Pythonie, zgodnie z zasadami SOLID i dobrymi praktykami programowania.

# Uruchomienie programu

python -m src.main szukaj "nazwa filmu"

# lub

python -m src.main pobierz https://www.cda.pl/video/XXXXXXX

## Funkcjonalności

- Logowanie do konta CDA Premium
- Wyszukiwanie filmów na platformie
- Przeglądanie folderów CDA
- Pobieranie informacji o filmach
- Pobieranie filmów w wybranej jakości
- Zarządzanie pobranymi plikami

## Struktura projektu

Projekt został zorganizowany zgodnie z zasadami SOLID:

- **Zasada pojedynczej odpowiedzialności (SRP)**: Każda klasa ma jedną odpowiedzialność
- **Zasada otwarte-zamknięte (OCP)**: Kod jest otwarty na rozszerzenia, zamknięty na modyfikacje
- **Zasada podstawienia Liskov (LSP)**: Hierarchia wyjątków zapewnia poprawne zastępowanie
- **Zasada segregacji interfejsów (ISP)**: Interfejsy są małe i specyficzne
- **Zasada odwrócenia zależności (DIP)**: Abstrakcje nie zależą od szczegółów implementacji

```
cda-premium-downloader/
├── .gitignore                  # Ignorowanie plików tymczasowych i folderów
├── README.md                   # Dokumentacja projektu
├── requirements.txt            # Wymagane zależności
├── setup.py                    # Konfiguracja instalacji pakietu
├── szybkie_pobieranie.py       # Skrypt do szybkiego pobierania z parametrami
└── src/                        # Główny katalog kodu źródłowego
    ├── __init__.py             # Inicjalizacja pakietu src
    ├── main.py                 # Punkt wejścia dla aplikacji
    ├── config.py               # Globalna konfiguracja aplikacji
    ├── cli/                    # Interfejs wiersza poleceń
    │   ├── __init__.py         # Inicjalizacja pakietu cli
    │   ├── cli_parser.py       # Parser argumentów wiersza poleceń
    │   └── cli_handler.py      # Obsługa komend CLI
    ├── core/                   # Główna logika biznesowa
    │   ├── __init__.py         # Inicjalizacja pakietu core
    │   ├── auth.py             # Uwierzytelnianie
    │   ├── downloader.py       # Pobieranie filmów
    │   ├── search.py           # Wyszukiwanie filmów
    │   ├── video_info.py       # Pobieranie informacji o wideo
    │   └── file_manager.py     # Zarządzanie plikami
    └── utils/                  # Narzędzia pomocnicze
        ├── __init__.py         # Inicjalizacja pakietu utils
        ├── exceptions.py       # Definicje wyjątków
        └── helpers.py          # Funkcje pomocnicze
```

## Wymagania

- Python 3.6+
- Konto CDA Premium

## Instalacja

### Z repozytorium

1. Sklonuj repozytorium:

```bash
git clone https://github.com/twoja-nazwa-uzytkownika/cda-premium-downloader.git
cd cda-premium-downloader
```

2. Zainstaluj wymagane biblioteki:

```bash
pip install -r requirements.txt
```

3. Uruchom program:

```bash
python -m src.main [komenda] [argumenty]
```

### Instalacja jako pakiet

```bash
pip install .
```

Po instalacji można używać programu jako:

```bash
cda-downloader [komenda] [argumenty]
```

## Użycie

### Pobieranie filmu

```bash
python -m src.main pobierz https://www.cda.pl/video/XXXXXXX
```

Opcjonalnie można określić preferowaną jakość:

```bash
python -m src.main pobierz https://www.cda.pl/video/XXXXXXX -j 1080
```

Oraz katalog docelowy:

```bash
python -m src.main pobierz https://www.cda.pl/video/XXXXXXX -k /path/to/directory
```

### Wyszukiwanie filmów

```bash
python -m src.main szukaj "nazwa filmu"
```

Wyszukiwanie wszystkich filmów (nie tylko premium):

```bash
python -m src.main szukaj "nazwa filmu" -a
```

Przejście do konkretnej strony wyników:

```bash
python -m src.main szukaj "nazwa filmu" -s 2
```

### Przeglądanie folderu

```bash
python -m src.main folder FOLDER_ID
```

### Informacje o filmie

```bash
python -m src.main info https://www.cda.pl/video/XXXXXXX
```

## Notatka prawna

Program służy wyłącznie do pobierania treści, do których masz legalny dostęp poprzez wykupione konto CDA Premium. Korzystanie z programu do pobierania treści chronionych prawem autorskim bez odpowiednich uprawnień może naruszać regulamin serwisu CDA oraz obowiązujące przepisy prawa.

## Licencja

MIT

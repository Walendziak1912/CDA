@echo on
title Instalacja srodowiska Python

:: Przejdź do folderu nadrzędnego i zapisz ścieżkę
cd ..
set "PROJECT_ROOT=%CD%"

:: Czyszczenie ekranu
cls
echo =====================================
:: Pokazanie wersji Python
echo Lista dostepnych wersji Python:
py -0p

echo Wpisz numer wersji Python (np. 3.13) i nacisnij ENTER:
set /p python_version="> "
echo %GREEN% Wybrano wersje: %python_version%
echo =====================================

:: Sprawdzanie czy folder istnieje - z pełną ścieżką
if exist "%PROJECT_ROOT%\.venv" (
    rd /s /q "%PROJECT_ROOT%\.venv"
)
echo =====================================
:: Utwórz wirtualne środowisko
echo %GREEN% Tworzenie wirtualnego srodowiska dla Python %python_version%...
py -%python_version% -m venv "%PROJECT_ROOT%\.venv"
echo =====================================
:: Aktywuj środowisko
echo %GREEN% Aktywacja srodowiska...
call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ====================================
    echo BLAD: Nie udalo sie aktywowac srodowiska!
    echo ====================================
    echo.
    echo Nacisnij dowolny klawisz aby zamknac...
    pause > nul
    cmd /k
    exit /b 1
)
echo =====================================
:: Aktualizacja pip
echo Aktualizacja pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo ===================================================================
    echo BLAD: Nie udalo sie zaktualizowac pip!
    echo ====================================
    echo.
    echo Nacisnij dowolny klawisz aby zamknac...
    pause > nul
    cmd /k
    exit /b 1
)
echo ===================================================================
:: Instalacja wymagań z requirements.txt
if exist requirements.txt (
    echo Instalacja pakietow z requirements.txt...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ===================================================================
        echo BLAD: Nie udalo sie zainstalowac pakietow!
        echo ===================================================================
        echo.
        echo Nacisnij dowolny klawisz aby zamknac...
        pause > nul
        cmd /k
        exit /b 1
    )
) else (
    echo UWAGA: Plik requirements.txt nie zostal znaleziony.
)

echo ===================================================================
echo Instalacja zakonczona pomyslnie!
echo Aby aktywowac srodowisko, uzyj: .venv\Scripts\activate.bat
echo ===================================================================

echo.
echo Nacisnij dowolny klawisz aby zamknac...
pause > nul
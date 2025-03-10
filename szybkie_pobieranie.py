#!/usr/bin/env python
"""
Skrypt do szybkiego pobierania filmów z CDA Premium.
Przyjmuje login, hasło i link do filmu jako parametry.

Przykład użycia:
    python szybkie_pobieranie.py --login mojlogin --haslo mojehaslo --url https://www.cda.pl/video/XXXXXXX
    
    lub:
    
    python szybkie_pobieranie.py -l mojlogin -p mojehaslo -u https://www.cda.pl/video/XXXXXXX
"""
import argparse
import logging
import sys
import getpass
from pathlib import Path

from src.core.auth import AuthService
from src.core.downloader import DownloaderService
from src.core.video_info import VideoInfoService
from src.utils.exceptions import CDADownloaderException
import requests


def main():
    """
    Funkcja główna skryptu.
    
    Returns:
        Kod wyjścia
    """
    # Konfiguracja parsera argumentów
    parser = argparse.ArgumentParser(description="Szybkie pobieranie filmów z CDA Premium")
    
    parser.add_argument("-l", "--login", help="Login do konta CDA Premium")
    parser.add_argument("-p", "--haslo", help="Hasło do konta CDA Premium")
    parser.add_argument("-u", "--url", help="URL filmu do pobrania")
    parser.add_argument("-j", "--jakosc", help="Preferowana jakość (np. 1080, 720)", default=None)
    parser.add_argument("-k", "--katalog", help="Katalog docelowy do zapisania filmu", type=Path, default=None)
    parser.add_argument("-v", "--verbose", help="Szczegółowe logowanie", action="store_true")
    
    args = parser.parse_args()
    
    # Konfiguracja poziomu logowania
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Utworzenie sesji HTTP
    session = requests.Session()
    auth_service = AuthService(session)
    video_info_service = VideoInfoService(session)
    downloader_service = DownloaderService(session, video_info_service)
    
    try:
        # Jeśli katalog docelowy został podany, ustaw go
        if args.katalog:
            downloader_service.download_dir = args.katalog
        
        # Pobierz login i hasło jeśli nie podano
        login = args.login or input("Podaj login do CDA Premium: ")
        haslo = args.haslo or getpass.getpass("Podaj hasło do CDA Premium: ")
        
        # Pobierz URL jeśli nie podano
        url = args.url or input("Podaj URL filmu do pobrania: ")
        
        # Zaloguj się do CDA Premium
        logging.info(f"Logowanie jako: {login}")
        if not auth_service.login(login, haslo):
            logging.error("Logowanie nie powiodło się. Kończenie programu.")
            return 1
        
        logging.info("Logowanie udane!")
        
        # Pobierz film
        logging.info(f"Pobieranie filmu: {url}")
        filepath = downloader_service.download(url, args.jakosc)
        
        logging.info(f"Film został pobrany do: {filepath}")
        return 0
        
    except CDADownloaderException as e:
        logging.error(f"Błąd: {str(e)}")
        return 1
    except KeyboardInterrupt:
        logging.info("Anulowano przez użytkownika")
        return 130
    finally:
        # Wyloguj się, jeśli zalogowano
        if auth_service.logged_in:
            auth_service.logout()


if __name__ == "__main__":
    sys.exit(main())
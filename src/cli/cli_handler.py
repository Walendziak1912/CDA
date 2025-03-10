"""
Obsługa komend wiersza poleceń dla aplikacji CDA Downloader.
"""
import getpass
import logging
import sys
import time
from pathlib import Path
from typing import Optional, List, Tuple

import requests
from tqdm import tqdm

from ..core.auth import AuthService
from ..core.downloader import DownloaderService
from ..core.search import SearchService, SearchResult
from ..core.video_info import VideoInfoService
from ..core.file_manager import FileManager
from ..utils import (
    CDADownloaderException, 
    AuthenticationError, 
    TokenError,
    VideoInfoError, 
    DownloadError,
    SearchError, 
    FileError
)


class CLIHandler:
    """Klasa obsługująca komendy wiersza poleceń."""
    
    def __init__(self):
        """Inicjalizacja obsługi komend."""
        self.session = requests.Session()
        self.auth_service = AuthService(self.session)
        self.video_info_service = VideoInfoService(self.session)
        self.search_service = SearchService(self.session)
        self.file_manager = FileManager()
        self.downloader_service = DownloaderService(
            self.session,
            self.video_info_service
        )
    
    def handle_command(self, args) -> int:
        """
        Obsługuje komendę na podstawie argumentów.
        
        Args:
            args: Sparsowane argumenty
            
        Returns:
            Kod wyjścia (0 - sukces, inny - błąd)
        """
        # Konfiguracja poziomu logowania
        log_level = logging.DEBUG if args.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        try:
            # Zaloguj się, jeśli nie wybrano opcji no_login
            if not args.no_login:
                self._login()
            
            # Obsługa konkretnych komend
            if args.command == 'pobierz':
                self._handle_download(args)
            elif args.command == 'szukaj':
                self._handle_search(args)
            elif args.command == 'folder':
                self._handle_folder(args)
            elif args.command == 'pobierz-folder':
                self._handle_download_folder(args)
            elif args.command == 'info':
                self._handle_info(args)
            else:
                logging.error(f"Nieznana komenda: {args.command}")
                return 1
                
            return 0
        except CDADownloaderException as e:
            logging.error(f"Błąd: {str(e)}")
            return 1
        except KeyboardInterrupt:
            logging.info("Anulowano przez użytkownika")
            return 130
        finally:
            # Wyloguj się, jeśli zalogowano
            if not args.no_login and self.auth_service.logged_in:
                self.auth_service.logout()
    
    def _login(self) -> None:
        """
        Loguje do konta CDA Premium.
        
        Raises:
            SystemExit: Gdy logowanie nie powiedzie się
        """
        username = input("Podaj login do CDA Premium: ")
        password = getpass.getpass("Podaj hasło do CDA Premium: ")
        
        if not self.auth_service.login(username, password):
            logging.error("Logowanie nie powiodło się. Kończenie programu.")
            sys.exit(1)
    
    def _handle_download(self, args) -> None:
        """
        Obsługuje komendę 'pobierz'.
        
        Args:
            args: Sparsowane argumenty
        """
        logging.info(f"Pobieranie filmu: {args.url}")
        
        # Ustaw katalog docelowy, jeśli podano
        if args.katalog:
            self.downloader_service.download_dir = args.katalog
        
        # Pobierz film
        filepath = self.downloader_service.download(args.url, args.jakosc)
        
        logging.info(f"Film został pobrany do: {filepath}")
    
    def _handle_search(self, args) -> None:
        """
        Obsługuje komendę 'szukaj'.
        
        Args:
            args: Sparsowane argumenty
        """
        premium_only = not args.wszystkie
        logging.info(f"Wyszukiwanie: '{args.zapytanie}', tylko premium: {premium_only}, strona: {args.strona}")
        
        # Wyszukaj filmy
        results = self.search_service.search(
            args.zapytanie,
            premium_only=premium_only,
            page=args.strona
        )
        
        self._display_search_results(results)
        
        # Zaproponuj pobranie filmu
        self._handle_search_selection(results)
    
    def _handle_folder(self, args) -> None:
        """
        Obsługuje komendę 'folder'.
        
        Args:
            args: Sparsowane argumenty
        """
        logging.info(f"Wyszukiwanie w folderze: {args.id}, strona: {args.strona}")
        
        # Wyszukaj filmy w folderze
        results = self.search_service.search_in_folder(
            args.id,
            page=args.strona
        )
        
        self._display_search_results(results)
        
        # Jeśli wybrano opcję pobierania wszystkich filmów
        if args.pobierz_wszystkie:
            logging.info("Rozpoczynam pobieranie wszystkich filmów z folderu...")
            self._download_all_from_results(results, args.jakosc, args.katalog)
        else:
            # Zaproponuj pobranie pojedynczego filmu
            self._handle_search_selection(results)
    
    def _handle_info(self, args) -> None:
        """
        Obsługuje komendę 'info'.
        
        Args:
            args: Sparsowane argumenty
        """
        logging.info(f"Pobieranie informacji o filmie: {args.url}")
        
        # Pobierz informacje o filmie
        video_info = self.video_info_service.get_video_info(args.url)
        
        # Wyświetl informacje
        print(f"\nInformacje o filmie:")
        print(f"Tytuł: {video_info.title}")
        print(f"ID: {video_info.video_id}")
        
        if video_info.author:
            print(f"Autor: {video_info.author}")
            
        if video_info.duration:
            print(f"Czas trwania: {video_info.duration}")
            
        if video_info.views:
            print(f"Wyświetlenia: {video_info.views}")
        
        print("\nDostępne jakości:")
        for quality, url in sorted(video_info.download_links.items()):
            print(f"- {quality}")
        
        # Zaproponuj pobranie filmu
        choice = input("\nCzy chcesz pobrać ten film? (t/n): ")
        if choice.lower() in ('t', 'tak'):
            quality = input("Podaj preferowaną jakość lub naciśnij Enter dla najlepszej dostępnej: ")
            
            # Pobierz film
            filepath = self.downloader_service.download(args.url, quality if quality else None)
            logging.info(f"Film został pobrany do: {filepath}")
    
    def _handle_download_folder(self, args) -> None:
        """
        Obsługuje komendę 'pobierz-folder'.
        
        Args:
            args: Sparsowane argumenty
        """
        # Ustaw katalog docelowy, jeśli podano
        if args.katalog:
            self.downloader_service.download_dir = args.katalog
        
        # Pobierz wszystkie filmy z folderu
        self._download_folder(
            folder_id=args.id,
            quality=args.jakosc,
            start_page=args.strona_start,
            end_page=args.strona_koniec,
            premium_only=args.tylko_filmy_premium
        )
    
    def _download_folder(self, folder_id: str, quality: Optional[str] = None, 
                         start_page: int = 1, end_page: Optional[int] = None,
                         premium_only: bool = False) -> None:
        """
        Pobiera wszystkie filmy z folderu CDA.
        
        Args:
            folder_id: ID folderu CDA
            quality: Preferowana jakość filmów
            start_page: Numer strony od której zacząć pobieranie
            end_page: Numer strony na której zakończyć pobieranie (domyślnie: wszystkie)
            premium_only: Czy pobierać tylko filmy premium
        """
        current_page = start_page
        total_downloaded = 0
        total_skipped = 0
        
        print(f"\nRozpoczynam pobieranie filmów z folderu {folder_id}")
        print(f"Strona początkowa: {start_page}")
        if end_page:
            print(f"Strona końcowa: {end_page}")
        else:
            print("Pobieranie wszystkich dostępnych stron")
        
        while True:
            logging.info(f"Pobieranie filmów ze strony {current_page}...")
            
            # Pobierz wyniki z bieżącej strony
            try:
                results = self.search_service.search_in_folder(folder_id, page=current_page)
            except SearchError as e:
                logging.error(f"Błąd podczas pobierania strony {current_page}: {str(e)}")
                break
            
            # Jeśli nie ma więcej wyników, zakończ
            if not results:
                logging.info(f"Brak filmów na stronie {current_page}. Kończenie pobierania.")
                break
            
            # Filtruj tylko filmy premium, jeśli wybrano taką opcję
            if premium_only:
                filtered_results = [r for r in results if r.premium]
                skipped_count = len(results) - len(filtered_results)
                results = filtered_results
                if skipped_count > 0:
                    logging.info(f"Pominięto {skipped_count} filmów nie-premium na stronie {current_page}")
                    total_skipped += skipped_count
            
            # Wyświetl informacje o filmach na bieżącej stronie
            print(f"\nZnaleziono {len(results)} filmów na stronie {current_page}:")
            for i, result in enumerate(results, 1):
                premium_tag = "[PREMIUM]" if result.premium else ""
                print(f"{i}. {result.title} {premium_tag}")
            
            # Pobierz wszystkie filmy z bieżącej strony
            downloaded, skipped = self._download_all_from_results(results, quality)
            total_downloaded += downloaded
            total_skipped += skipped
            
            # Przejdź do następnej strony
            current_page += 1
            
            # Zakończ, jeśli osiągnięto stronę końcową
            if end_page and current_page > end_page:
                logging.info(f"Osiągnięto stronę końcową {end_page}. Kończenie pobierania.")
                break
            
            # Zrób małą przerwę między stronami, aby nie przeciążać serwera
            time.sleep(2)
        
        print(f"\nZakończono pobieranie folderu {folder_id}")
        print(f"Pobrano filmów: {total_downloaded}")
        print(f"Pominięto filmów: {total_skipped}")
    
    def _download_all_from_results(self, results: List[SearchResult], 
                                   quality: Optional[str] = None,
                                   download_dir: Optional[Path] = None) -> Tuple[int, int]:
        """
        Pobiera wszystkie filmy z listy wyników.
        
        Args:
            results: Lista wyników wyszukiwania
            quality: Preferowana jakość filmów
            download_dir: Katalog docelowy do zapisania filmów
            
        Returns:
            Krotka (liczba pobranych, liczba pominiętych)
        """
        if not results:
            return 0, 0
        
        # Ustaw katalog docelowy, jeśli podano
        if download_dir:
            original_download_dir = self.downloader_service.download_dir
            self.downloader_service.download_dir = download_dir
        
        downloaded = 0
        skipped = 0
        
        # Utwórz pasek postępu
        progress_bar = tqdm(total=len(results), desc="Pobieranie filmów")
        
        try:
            for i, result in enumerate(results, 1):
                try:
                    # Aktualizuj opis paska postępu
                    progress_bar.set_description(f"Pobieranie {i}/{len(results)}: {result.title[:30]}...")
                    
                    # Pobierz film
                    logging.info(f"Pobieranie filmu {i}/{len(results)}: {result.title}")
                    filepath = self.downloader_service.download(result.url, quality)
                    logging.info(f"Film {result.title} został pobrany do: {filepath}")
                    downloaded += 1
                except (VideoInfoError, DownloadError, FileError) as e:
                    logging.error(f"Błąd podczas pobierania filmu {result.title}: {str(e)}")
                    skipped += 1
                
                progress_bar.update(1)
                
                # Zrób małą przerwę między pobieraniami, aby nie przeciążać serwera
                if i < len(results):
                    time.sleep(1)
        finally:
            # Zamknij pasek postępu
            progress_bar.close()
            
            # Przywróć oryginalny katalog docelowy, jeśli został zmieniony
            if download_dir:
                self.downloader_service.download_dir = original_download_dir
        
        logging.info(f"Zakończono pobieranie {downloaded} filmów (pominięto {skipped})")
        return downloaded, skipped
    
    def _display_search_results(self, results: List[SearchResult]) -> None:
        """
        Wyświetla wyniki wyszukiwania.
        
        Args:
            results: Lista wyników wyszukiwania
        """
        if not results:
            print("Nie znaleziono żadnych wyników.")
            return
        
        print(f"\nZnaleziono {len(results)} wyników:")
        for i, result in enumerate(results, 1):
            premium_tag = "[PREMIUM]" if result.premium else ""
            print(f"{i}. {result.title} {premium_tag}")
            
            if result.author:
                print(f"   Autor: {result.author}")
                
            if result.duration:
                print(f"   Czas trwania: {result.duration}")
                
            if result.views:
                print(f"   Wyświetlenia: {result.views}")
                
            print(f"   URL: {result.url}")
            print()
    
    def _handle_search_selection(self, results: List[SearchResult]) -> None:
        """
        Obsługuje wybór filmu z wyników wyszukiwania.
        
        Args:
            results: Lista wyników wyszukiwania
        """
        if not results:
            return
            
        while True:
            try:
                choice = input("\nPodaj numer filmu do pobrania (lub 'q' aby wyjść, 'a' aby pobrać wszystkie): ")
                
                # Wyjście
                if choice.lower() in ('q', 'quit', 'exit', 'wyjdź', 'wyjdz'):
                    break
                
                # Pobieranie wszystkich filmów
                if choice.lower() in ('a', 'all', 'wszystkie'):
                    quality = input("Podaj preferowaną jakość dla wszystkich filmów (lub naciśnij Enter dla najlepszej dostępnej): ")
                    self._download_all_from_results(results, quality if quality else None)
                    break
                
                # Pobieranie pojedynczego filmu
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(results):
                    selected = results[choice_idx]
                    print(f"Wybrano: {selected.title}")
                    
                    # Pozwól wybrać jakość
                    quality = input("Podaj preferowaną jakość (np. 1080, 720) lub naciśnij Enter dla najlepszej dostępnej: ")
                    
                    # Pobierz film
                    filepath = self.downloader_service.download(selected.url, quality if quality else None)
                    logging.info(f"Film został pobrany do: {filepath}")
                    
                    # Zapytaj, czy użytkownik chce pobrać kolejny film
                    choice = input("\nCzy chcesz pobrać kolejny film? (t/n): ")
                    if choice.lower() not in ('t', 'tak'):
                        break
                else:
                    print("Nieprawidłowy numer. Spróbuj ponownie.")
            except ValueError:
                print("Wprowadź poprawny numer.")
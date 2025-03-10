#!/usr/bin/env python
"""
Interaktywny skrypt uruchamiający aplikację CDA Downloader.
Wyświetla menu z opcjami i umożliwia wybór operacji bez konieczności
używania argumentów wiersza poleceń.
"""
import os
import sys
import getpass
import requests
from pathlib import Path

from src.core.auth import AuthService
from src.core.downloader import DownloaderService
from src.core.search import SearchService
from src.core.video_info import VideoInfoService
from src.core.file_manager import FileManager
from src.utils import CDADownloaderException


class InteractiveRunner:
    """Klasa obsługująca interaktywne menu aplikacji."""
    
    def __init__(self):
        """Inicjalizacja interaktywnego menu."""
        self.session = requests.Session()
        self.auth_service = AuthService(self.session)
        self.video_info_service = VideoInfoService(self.session)
        self.search_service = SearchService(self.session)
        self.file_manager = FileManager()
        self.downloader_service = DownloaderService(
            self.session,
            self.video_info_service
        )
        self.logged_in = False
        self.login_CDA = ""
        self.password_CDA = ""
        
    def clear_screen(self):
        """Czyści ekran terminala."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        """Wyświetla nagłówek aplikacji."""
        self.clear_screen()
        print("=" * 60)
        print("                 CDA PREMIUM DOWNLOADER                 ")
        print("=" * 60)
        
        if self.logged_in:
            print(f"Zalogowano jako: {self.auth_service.username}")
        else:
            print("Status: Niezalogowany")
        print("-" * 60)
        
    def print_menu(self):
        """Wyświetla główne menu aplikacji."""
        self.print_header()
        
        print("MENU GŁÓWNE:")
        if not self.logged_in:
            print("1. Zaloguj się do CDA Premium")
        else:
            print("1. Pobierz film")
            print("2. Wyszukaj filmy")
            print("3. Przeglądaj folder")
            print("4. Pobierz cały folder")
            print("5. Informacje o filmie")
            print("6. Wyloguj się")
        
        print("0. Wyjdź z programu")
        print("-" * 60)
        
    def run(self):
        """Uruchamia interaktywne menu aplikacji."""
        try:
            while True:
                self.print_menu()
                
                try:
                    choice = input("Wybierz opcję: ")
                    
                    # Opcja wyjścia
                    if choice == '0':
                        self.clear_screen()
                        print("Dziękujemy za skorzystanie z programu CDA Premium Downloader!")
                        break
                    
                    if not self.logged_in:
                        if choice == '1':
                            self.login()
                        else:
                            print("\nNieprawidłowy wybór. Naciśnij Enter, aby kontynuować...")
                            input()
                    else:
                        if choice == '1':
                            self.download_video()
                        elif choice == '2':
                            self.search_videos()
                        elif choice == '3':
                            self.browse_folder()
                        elif choice == '4':
                            self.download_folder()
                        elif choice == '5':
                            self.show_video_info()
                        elif choice == '6':
                            self.logout()
                        else:
                            print("\nNieprawidłowy wybór. Naciśnij Enter, aby kontynuować...")
                            input()
                            
                except KeyboardInterrupt:
                    self.clear_screen()
                    print("\nOperacja anulowana przez użytkownika.")
                    input("Naciśnij Enter, aby kontynuować...")
                    
        except Exception as e:
            self.clear_screen()

            print(f"Wystąpił nieoczekiwany błąd: {str(e)}")
            input("Naciśnij Enter, aby kontynuować...")
        finally:
            # Wyloguj się, jeśli zalogowano
            if self.logged_in:
                self.auth_service.logout()
    
    def login(self):
        """Logowanie do konta CDA Premium."""
        self.print_header()
        print("LOGOWANIE DO CDA PREMIUM")
        print("-" * 60)
        
        if(not(self.login_CDA and self.password_CDA)):
            self.login_CDA = input("Podaj login do CDA Premium: ")
            self.password_CDA = getpass.getpass("Podaj hasło do CDA Premium: ")
        
        print("\nLogowanie...")
        
        try:
            if self.auth_service.login(self.login_CDA, self.password_CDA):
                self.logged_in = True
                print("\nLogowanie udane!")
            else:
                print("\nLogowanie nieudane. Sprawdź dane logowania.")
        except CDADownloaderException as e:
            print(f"\nBłąd podczas logowania: {str(e)}")
            
        input("\nNaciśnij Enter, aby kontynuować...")
    
    def logout(self):
        """Wylogowanie z konta CDA Premium."""
        self.print_header()
        print("WYLOGOWYWANIE")
        print("-" * 60)
        
        try:
            if self.auth_service.logout():
                self.logged_in = False
                print("Wylogowano pomyślnie.")
            else:
                print("Wystąpił błąd podczas wylogowywania.")
        except CDADownloaderException as e:
            print(f"Błąd podczas wylogowywania: {str(e)}")
            
        input("\nNaciśnij Enter, aby kontynuować...")
    
    def download_video(self):
        """Pobieranie pojedynczego filmu."""
        self.print_header()
        print("POBIERANIE FILMU")
        print("-" * 60)
        
        url = input("Podaj URL filmu do pobrania: ")
        
        if not url:
            print("URL nie może być pusty.")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
            
        quality = input("Podaj preferowaną jakość (np. 1080, 720) lub naciśnij Enter dla najlepszej dostępnej: ")
        
        # Opcjonalnie zmień katalog docelowy
        change_dir = input("Czy chcesz zmienić katalog docelowy? (t/n): ")
        if change_dir.lower() in ('t', 'tak'):
            download_dir = input("Podaj ścieżkę do katalogu docelowego: ")
            if download_dir:
                self.downloader_service.download_dir = Path(download_dir)
        
        try:
            print(f"\nPobieranie filmu: {url}")
            filepath = self.downloader_service.download(url, quality if quality else None)
            print(f"\nFilm został pobrany do: {filepath}")
        except CDADownloaderException as e:
            print(f"\nBłąd podczas pobierania filmu: {str(e)}")
            
        input("\nNaciśnij Enter, aby kontynuować...")
    
    def search_videos(self):
        """Wyszukiwanie filmów."""
        self.print_header()
        print("WYSZUKIWANIE FILMÓW")
        print("-" * 60)
        
        query = input("Podaj frazę do wyszukania: ")
        
        if not query:
            print("Fraza wyszukiwania nie może być pusta.")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
            
        premium_only = input("Wyszukiwać tylko filmy premium? (t/n): ").lower() in ('t', 'tak')
        
        try:
            print(f"\nWyszukiwanie: '{query}', tylko premium: {premium_only}")
            results = self.search_service.search(query, premium_only=premium_only)
            
            if not results:
                print("\nNie znaleziono żadnych wyników.")
                input("\nNaciśnij Enter, aby kontynuować...")
                return
                
            self.display_search_results(results)
            self.handle_search_selection(results)
        except CDADownloaderException as e:
            print(f"\nBłąd podczas wyszukiwania: {str(e)}")
            input("\nNaciśnij Enter, aby kontynuować...")
    
    def browse_folder(self):
        """Przeglądanie folderu CDA."""
        self.print_header()
        print("PRZEGLĄDANIE FOLDERU")
        print("-" * 60)
        
        folder_id = input("Podaj ID folderu CDA: ")
        
        if not folder_id:
            print("ID folderu nie może być puste.")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
            
        try:
            print(f"\nWyszukiwanie w folderze: {folder_id}")
            results = self.search_service.search_in_folder(folder_id)
            
            if not results:
                print("\nNie znaleziono żadnych filmów w folderze.")
                input("\nNaciśnij Enter, aby kontynuować...")
                return
                
            self.display_search_results(results)
            
            # Opcja pobierania wszystkich filmów
            download_all = input("\nCzy chcesz pobrać wszystkie filmy z folderu? (t/n): ").lower() in ('t', 'tak')
            
            if download_all:
                quality = input("Podaj preferowaną jakość dla wszystkich filmów lub naciśnij Enter dla najlepszej dostępnej: ")
                
                # Opcjonalnie zmień katalog docelowy
                change_dir = input("Czy chcesz zmienić katalog docelowy? (t/n): ")
                download_dir = None
                if change_dir.lower() in ('t', 'tak'):
                    download_dir_input = input("Podaj ścieżkę do katalogu docelowego: ")
                    if download_dir_input:
                        download_dir = Path(download_dir_input)
                
                self.download_all_from_results(results, quality if quality else None, download_dir)
            else:
                self.handle_search_selection(results)
        except CDADownloaderException as e:
            print(f"\nBłąd podczas przeglądania folderu: {str(e)}")
            input("\nNaciśnij Enter, aby kontynuować...")
    
    def download_folder(self):
        """Pobieranie całego folderu CDA."""
        self.print_header()
        print("POBIERANIE CAŁEGO FOLDERU")
        print("-" * 60)
        
        folder_id = input("Podaj ID folderu CDA: ")
        
        if not folder_id:
            print("ID folderu nie może być puste.")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
            
        quality = input("Podaj preferowaną jakość dla wszystkich filmów lub naciśnij Enter dla najlepszej dostępnej: ")
        
        # Opcjonalnie zmień katalog docelowy
        change_dir = input("Czy chcesz zmienić katalog docelowy? (t/n): ")
        download_dir = None
        if change_dir.lower() in ('t', 'tak'):
            download_dir_input = input("Podaj ścieżkę do katalogu docelowego: ")
            if download_dir_input:
                download_dir = Path(download_dir_input)
                self.downloader_service.download_dir = download_dir
        
        premium_only = input("Pobierać tylko filmy premium? (t/n): ").lower() in ('t', 'tak')
        
        start_page = 1
        try:
            start_page_input = input("Od której strony zacząć pobieranie? (domyślnie: 1): ")
            if start_page_input:
                start_page = int(start_page_input)
        except ValueError:
            print("Nieprawidłowy numer strony. Ustawiam na 1.")
            start_page = 1
        
        end_page = None
        try:
            end_page_input = input("Na której stronie zakończyć pobieranie? (domyślnie: wszystkie): ")
            if end_page_input:
                end_page = int(end_page_input)
        except ValueError:
            print("Nieprawidłowy numer strony. Ustawiam na wszystkie strony.")
            end_page = None
        
        try:
            self.download_folder_impl(
                folder_id=folder_id,
                quality=quality if quality else None,
                start_page=start_page,
                end_page=end_page,
                premium_only=premium_only
            )
        except CDADownloaderException as e:
            print(f"\nBłąd podczas pobierania folderu: {str(e)}")
            
        input("\nNaciśnij Enter, aby kontynuować...")
    
    def show_video_info(self):
        """Wyświetlanie informacji o filmie."""
        self.print_header()
        print("INFORMACJE O FILMIE")
        print("-" * 60)
        
        url = input("Podaj URL filmu: ")
        
        if not url:
            print("URL nie może być pusty.")
            input("\nNaciśnij Enter, aby kontynuować...")
            return
            
        try:
            print(f"\nPobieranie informacji o filmie: {url}")
            video_info = self.video_info_service.get_video_info(url)
            
            print("\nInformacje o filmie:")
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
            download = input("\nCzy chcesz pobrać ten film? (t/n): ").lower() in ('t', 'tak')
            
            if download:
                quality = input("Podaj preferowaną jakość lub naciśnij Enter dla najlepszej dostępnej: ")
                
                # Pobierz film
                filepath = self.downloader_service.download(url, quality if quality else None)
                print(f"\nFilm został pobrany do: {filepath}")
                
        except CDADownloaderException as e:
            print(f"\nBłąd podczas pobierania informacji o filmie: {str(e)}")
            
        input("\nNaciśnij Enter, aby kontynuować...")
    
    def display_search_results(self, results):
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
    
    def handle_search_selection(self, results):
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
                    
                    # Opcjonalnie zmień katalog docelowy
                    change_dir = input("Czy chcesz zmienić katalog docelowy? (t/n): ")
                    download_dir = None
                    if change_dir.lower() in ('t', 'tak'):
                        download_dir_input = input("Podaj ścieżkę do katalogu docelowego: ")
                        if download_dir_input:
                            download_dir = Path(download_dir_input)
                    
                    self.download_all_from_results(results, quality if quality else None, download_dir)
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
                    print(f"\nFilm został pobrany do: {filepath}")
                    
                    # Zapytaj, czy użytkownik chce pobrać kolejny film
                    download_another = input("\nCzy chcesz pobrać kolejny film? (t/n): ").lower() in ('t', 'tak')
                    if not download_another:
                        break
                else:
                    print("Nieprawidłowy numer. Spróbuj ponownie.")
            except ValueError:
                print("Wprowadź poprawny numer.")
    
    def download_all_from_results(self, results, quality=None, download_dir=None):
        """
        Pobiera wszystkie filmy z listy wyników.
        
        Args:
            results: Lista wyników wyszukiwania
            quality: Preferowana jakość filmów
            download_dir: Katalog docelowy do zapisania filmów
        """
        if not results:
            print("Brak filmów do pobrania.")
            return
            
        # Ustaw katalog docelowy, jeśli podano
        original_download_dir = None
        if download_dir:
            original_download_dir = self.downloader_service.download_dir
            self.downloader_service.download_dir = download_dir
            
        downloaded = 0
        skipped = 0
        
        print(f"\nRozpoczynam pobieranie {len(results)} filmów:")
        
        try:
            for i, result in enumerate(results, 1):
                try:
                    print(f"\n{i}/{len(results)}: Pobieranie: {result.title}")
                    
                    # Pobierz film
                    filepath = self.downloader_service.download(result.url, quality)
                    print(f"Film został pobrany do: {filepath}")
                    downloaded += 1
                except CDADownloaderException as e:
                    print(f"Błąd podczas pobierania filmu {result.title}: {str(e)}")
                    skipped += 1
                    
                # Krótka pauza między pobieraniami
                if i < len(results):
                    print("Pauza przed pobraniem następnego filmu...")
                    import time
                    time.sleep(1)
        finally:
            # Przywróć oryginalny katalog docelowy, jeśli został zmieniony
            if original_download_dir:
                self.downloader_service.download_dir = original_download_dir
        
        print(f"\nZakończono pobieranie filmów.")
        print(f"Pobrano filmów: {downloaded}")
        print(f"Pominięto filmów: {skipped}")
    
    def download_folder_impl(self, folder_id, quality=None, start_page=1, end_page=None, premium_only=False):
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
            print(f"\nPobieranie filmów ze strony {current_page}...")
            
            # Pobierz wyniki z bieżącej strony
            try:
                results = self.search_service.search_in_folder(folder_id, page=current_page)
            except CDADownloaderException as e:
                print(f"Błąd podczas pobierania strony {current_page}: {str(e)}")
                break
            
            # Jeśli nie ma więcej wyników, zakończ
            if not results:
                print(f"Brak filmów na stronie {current_page}. Kończenie pobierania.")
                break
            
            # Filtruj tylko filmy premium, jeśli wybrano taką opcję
            if premium_only:
                filtered_results = [r for r in results if r.premium]
                skipped_count = len(results) - len(filtered_results)
                results = filtered_results
                if skipped_count > 0:
                    print(f"Pominięto {skipped_count} filmów nie-premium na stronie {current_page}")
                    total_skipped += skipped_count
            
            # Wyświetl informacje o filmach na bieżącej stronie
            print(f"\nZnaleziono {len(results)} filmów na stronie {current_page}:")
            for i, result in enumerate(results, 1):
                premium_tag = "[PREMIUM]" if result.premium else ""
                print(f"{i}. {result.title} {premium_tag}")
            
            # Pobierz wszystkie filmy z bieżącej strony
            for i, result in enumerate(results, 1):
                try:
                    print(f"\nPobieranie filmu {i}/{len(results)} ze strony {current_page}: {result.title}")
                    filepath = self.downloader_service.download(result.url, quality)
                    print(f"Film został pobrany do: {filepath}")
                    total_downloaded += 1
                except CDADownloaderException as e:
                    print(f"Błąd podczas pobierania filmu {result.title}: {str(e)}")
                    total_skipped += 1
                
                # Krótka pauza między pobieraniami
                if i < len(results):
                    print("Pauza przed pobraniem następnego filmu...")
                    import time
                    time.sleep(1)
            
            # Przejdź do następnej strony
            current_page += 1
            
            # Zakończ, jeśli osiągnięto stronę końcową
            if end_page and current_page > end_page:
                print(f"Osiągnięto stronę końcową {end_page}. Kończenie pobierania.")
                break
            
            # Zrób małą przerwę między stronami, aby nie przeciążać serwera
            print("\nPrzechodzenie do następnej strony...")
            import time
            time.sleep(2)
        
        print(f"\nZakończono pobieranie folderu {folder_id}")
        print(f"Pobrano filmów: {total_downloaded}")
        print(f"Pominięto filmów: {total_skipped}")


if __name__ == "__main__":
    runner = InteractiveRunner()
    runner.run()
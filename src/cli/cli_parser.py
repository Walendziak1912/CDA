"""
Parser argumentów wiersza poleceń dla aplikacji CDA Downloader.
"""
import argparse
from pathlib import Path
from typing import Optional


class CLIParser:
    """Klasa analizująca argumenty wiersza poleceń."""
    
    def __init__(self):
        """Inicjalizacja parsera argumentów."""
        self.parser = argparse.ArgumentParser(
            description='Program do pobierania filmów z CDA Premium.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self._setup_parsers()
    
    def _setup_parsers(self) -> None:
        """Konfiguracja parsera argumentów."""
        subparsers = self.parser.add_subparsers(
            dest='command',
            help='Dostępne komendy',
            required=True
        )
        
        # Parser dla komendy 'pobierz'
        download_parser = subparsers.add_parser(
            'pobierz',
            help='Pobierz film z CDA'
        )
        download_parser.add_argument(
            'url',
            help='URL filmu do pobrania'
        )
        download_parser.add_argument(
            '-j', '--jakosc',
            help='Preferowana jakość (np. 1080, 720)',
            default=None
        )
        download_parser.add_argument(
            '-k', '--katalog',
            help='Katalog docelowy do zapisania filmu',
            type=Path,
            default=None
        )
        
        # Parser dla komendy 'szukaj'
        search_parser = subparsers.add_parser(
            'szukaj',
            help='Wyszukaj filmy na CDA'
        )
        search_parser.add_argument(
            'zapytanie',
            help='Fraza do wyszukania'
        )
        search_parser.add_argument(
            '-a', '--wszystkie',
            help='Wyszukaj wszystkie filmy (nie tylko premium)',
            action='store_true'
        )
        search_parser.add_argument(
            '-s', '--strona',
            help='Numer strony wyników',
            type=int,
            default=1
        )
        
        # Parser dla komendy 'folder'
        folder_parser = subparsers.add_parser(
            'folder',
            help='Wyszukaj filmy w folderze CDA'
        )
        folder_parser.add_argument(
            'id',
            help='ID folderu CDA'
        )
        folder_parser.add_argument(
            '-s', '--strona',
            help='Numer strony wyników',
            type=int,
            default=1
        )
        folder_parser.add_argument(
            '-p', '--pobierz-wszystkie',
            help='Pobierz wszystkie filmy z folderu',
            action='store_true'
        )
        folder_parser.add_argument(
            '-j', '--jakosc',
            help='Preferowana jakość dla wszystkich filmów (np. 1080, 720)',
            default=None
        )
        folder_parser.add_argument(
            '-k', '--katalog',
            help='Katalog docelowy do zapisania filmów',
            type=Path,
            default=None
        )
        
        # Parser dla komendy 'pobierz-folder'
        download_folder_parser = subparsers.add_parser(
            'pobierz-folder',
            help='Pobierz wszystkie filmy z folderu CDA'
        )
        download_folder_parser.add_argument(
            'id',
            help='ID folderu CDA'
        )
        download_folder_parser.add_argument(
            '-j', '--jakosc',
            help='Preferowana jakość dla wszystkich filmów (np. 1080, 720)',
            default=None
        )
        download_folder_parser.add_argument(
            '-k', '--katalog',
            help='Katalog docelowy do zapisania filmów',
            type=Path,
            default=None
        )
        download_folder_parser.add_argument(
            '-s', '--strona-start',
            help='Numer strony od której zacząć pobieranie',
            type=int,
            default=1
        )
        download_folder_parser.add_argument(
            '-e', '--strona-koniec',
            help='Numer strony na której zakończyć pobieranie (domyślnie: wszystkie)',
            type=int,
            default=None
        )
        download_folder_parser.add_argument(
            '-f', '--tylko-filmy-premium',
            help='Pobieraj tylko filmy premium',
            action='store_true'
        )
        
        # Parser dla komendy 'info'
        info_parser = subparsers.add_parser(
            'info',
            help='Pobierz informacje o filmie bez pobierania'
        )
        info_parser.add_argument(
            'url',
            help='URL filmu'
        )
        
        # Opcje globalne
        self.parser.add_argument(
            '-v', '--verbose',
            help='Szczegółowe logowanie',
            action='store_true'
        )
        self.parser.add_argument(
            '--no-login',
            help='Nie loguj się (ograniczona funkcjonalność)',
            action='store_true',
            dest='no_login'
        )
    
    def parse_args(self, args: Optional[list] = None):
        """
        Parsuje argumenty wiersza poleceń.
        
        Args:
            args: Argumenty do sparsowania (opcjonalnie)
            
        Returns:
            Sparsowane argumenty
        """
        return self.parser.parse_args(args)
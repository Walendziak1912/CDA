"""
Główny punkt wejścia dla aplikacji CDA Downloader.
"""
import sys
import logging

from .cli.cli_parser import CLIParser
from .cli.cli_handler import CLIHandler


def main():
    """
    Funkcja główna aplikacji.
    
    Returns:
        Kod wyjścia
    """
    try:
        # Utwórz parser argumentów i obsługę CLI
        parser = CLIParser()
        handler = CLIHandler()
        
        # Parsuj argumenty wiersza poleceń
        args = parser.parse_args()
        
        # Obsłuż komendę
        return handler.handle_command(args)
    except Exception as e:
        logging.error(f"Nieobsłużony błąd: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
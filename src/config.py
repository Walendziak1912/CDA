"""
Konfiguracja aplikacji CDA Downloader.
"""
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Klasa zawierająca konfigurację aplikacji."""
    base_url: str = "https://www.cda.pl"
    login_url: str = "https://www.cda.pl/login"
    download_folder: Path = Path(os.getcwd()) / "pobrane_filmy"
    chunk_size: int = 1024 * 1024  # 1MB
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )
    
    def __post_init__(self):
        """Inicjalizacja po utworzeniu obiektu."""
        # Utwórz folder na pobrane filmy, jeśli nie istnieje
        self.download_folder.mkdir(parents=True, exist_ok=True)
    
    @property
    def headers(self) -> dict:
        """Domyślne nagłówki HTTP."""
        return {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        }


# Domyślna konfiguracja aplikacji
config = Config()
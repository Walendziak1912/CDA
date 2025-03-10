"""
Moduł odpowiedzialny za zarządzanie plikami.
"""
import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional

from ..config import config
from ..utils.exceptions import FileError


class FileManager:
    """Klasa zarządzająca plikami."""
    
    def __init__(self, download_dir: Optional[Path] = None):
        """
        Inicjalizacja menedżera plików.
        
        Args:
            download_dir: Katalog do pobierania (opcjonalnie)
        """
        self.download_dir = download_dir or config.download_folder
        self._ensure_download_dir()
    
    def _ensure_download_dir(self) -> None:
        """
        Upewnia się, że katalog do pobierania istnieje.
        
        Raises:
            FileError: Gdy nie można utworzyć katalogu
        """
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise FileError(f"Nie można utworzyć katalogu {self.download_dir}: {str(e)}")
    
    def list_files(self, pattern: Optional[str] = None) -> List[Path]:
        """
        Zwraca listę plików w katalogu pobierania.
        
        Args:
            pattern: Wzorzec do filtrowania plików (opcjonalnie)
            
        Returns:
            Lista ścieżek do plików
            
        Raises:
            FileError: Gdy wystąpił błąd podczas listowania plików
        """
        try:
            self._ensure_download_dir()
            
            if pattern:
                return sorted(self.download_dir.glob(pattern))
            else:
                return sorted(p for p in self.download_dir.iterdir() if p.is_file())
        except Exception as e:
            raise FileError(f"Błąd podczas listowania plików: {str(e)}")
    
    def delete_file(self, filepath: Path) -> bool:
        """
        Usuwa plik.
        
        Args:
            filepath: Ścieżka do pliku
            
        Returns:
            True jeśli usunięto plik, False w przeciwnym razie
            
        Raises:
            FileError: Gdy wystąpił błąd podczas usuwania pliku
        """
        try:
            if not filepath.exists():
                logging.warning(f"Plik {filepath} nie istnieje")
                return False
                
            if not filepath.is_file():
                logging.warning(f"{filepath} nie jest plikiem")
                return False
                
            filepath.unlink()
            logging.info(f"Usunięto plik: {filepath}")
            return True
        except Exception as e:
            raise FileError(f"Błąd podczas usuwania pliku {filepath}: {str(e)}")
    
    def move_file(self, source: Path, destination: Path) -> Path:
        """
        Przenosi plik.
        
        Args:
            source: Ścieżka źródłowa
            destination: Ścieżka docelowa
            
        Returns:
            Ścieżka do przeniesionego pliku
            
        Raises:
            FileError: Gdy wystąpił błąd podczas przenoszenia pliku
        """
        try:
            if not source.exists():
                raise FileError(f"Plik źródłowy {source} nie istnieje")
                
            if not source.is_file():
                raise FileError(f"{source} nie jest plikiem")
                
            # Upewnij się, że katalog docelowy istnieje
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Przenieś plik
            shutil.move(str(source), str(destination))
            logging.info(f"Przeniesiono plik: {source} -> {destination}")
            
            return destination
        except Exception as e:
            raise FileError(f"Błąd podczas przenoszenia pliku: {str(e)}")
    
    def rename_file(self, filepath: Path, new_name: str) -> Path:
        """
        Zmienia nazwę pliku.
        
        Args:
            filepath: Ścieżka do pliku
            new_name: Nowa nazwa pliku
            
        Returns:
            Ścieżka do pliku po zmianie nazwy
            
        Raises:
            FileError: Gdy wystąpił błąd podczas zmiany nazwy pliku
        """
        try:
            if not filepath.exists():
                raise FileError(f"Plik {filepath} nie istnieje")
                
            if not filepath.is_file():
                raise FileError(f"{filepath} nie jest plikiem")
                
            new_path = filepath.parent / new_name
            filepath.rename(new_path)
            logging.info(f"Zmieniono nazwę pliku: {filepath} -> {new_path}")
            
            return new_path
        except Exception as e:
            raise FileError(f"Błąd podczas zmiany nazwy pliku: {str(e)}")
    
    def get_file_details(self, filepath: Path) -> dict:
        """
        Zwraca szczegóły pliku.
        
        Args:
            filepath: Ścieżka do pliku
            
        Returns:
            Słownik z informacjami o pliku
            
        Raises:
            FileError: Gdy wystąpił błąd podczas pobierania informacji o pliku
        """
        try:
            if not filepath.exists():
                raise FileError(f"Plik {filepath} nie istnieje")
                
            if not filepath.is_file():
                raise FileError(f"{filepath} nie jest plikiem")
                
            stats = filepath.stat()
            
            return {
                'name': filepath.name,
                'path': str(filepath),
                'size': stats.st_size,
                'created': stats.st_ctime,
                'modified': stats.st_mtime,
                'extension': filepath.suffix,
            }
        except Exception as e:
            raise FileError(f"Błąd podczas pobierania informacji o pliku: {str(e)}")
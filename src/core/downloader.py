"""
Moduł odpowiedzialny za pobieranie filmów z CDA.
"""
import logging
import os
from typing import Callable, Optional, Tuple
from pathlib import Path

import requests
from tqdm import tqdm

from ..config import config
from ..utils.exceptions import DownloadError, FileError
from ..utils.helpers import create_video_filename
from .video_info import VideoInfo, VideoInfoService


class DownloaderService:
    """Klasa obsługująca pobieranie wideo z CDA."""
    
    def __init__(
        self, 
        session: requests.Session,
        video_info_service: VideoInfoService,
        download_dir: Optional[Path] = None
    ):
        """
        Inicjalizacja serwisu pobierania.
        
        Args:
            session: Sesja HTTP (zalogowana)
            video_info_service: Serwis informacji o wideo
            download_dir: Katalog do pobierania (opcjonalnie)
        """
        self.session = session
        self.video_info_service = video_info_service
        self.download_dir = download_dir or config.download_folder
        
        # Upewnij się, że katalog istnieje
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    def download(
        self, 
        video_url: str, 
        preferred_quality: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Path:
        """
        Pobiera wideo z CDA.
        
        Args:
            video_url: URL wideo
            preferred_quality: Preferowana jakość (opcjonalnie)
            progress_callback: Callback do aktualizacji postępu (opcjonalnie)
            
        Returns:
            Ścieżka do pobranego pliku
            
        Raises:
            DownloadError: Gdy wystąpił błąd podczas pobierania
            FileError: Gdy wystąpił błąd podczas zapisywania pliku
        """
        try:
            # Pobierz informacje o wideo
            logging.info(f"Pobieranie informacji o wideo: {video_url}")
            video_info = self.video_info_service.get_video_info(video_url)
            
            # Wybierz jakość i pobierz link
            quality, download_url = self._select_quality(video_info, preferred_quality)
            
            # Utwórz nazwę pliku
            filename = create_video_filename(video_info.title, quality)
            filepath = self.download_dir / filename
            
            logging.info(f"Pobieranie: {video_info.title} w jakości {quality}")
            logging.info(f"Zapisywanie do: {filepath}")
            
            # Pobierz plik
            self._download_file(download_url, filepath, progress_callback)
            
            logging.info(f"Pobieranie zakończone: {filepath}")
            return filepath
            
        except Exception as e:
            raise DownloadError(f"Błąd podczas pobierania wideo: {str(e)}")
    
    def _select_quality(
        self, 
        video_info: VideoInfo, 
        preferred_quality: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Wybiera jakość do pobrania.
        
        Args:
            video_info: Informacje o wideo
            preferred_quality: Preferowana jakość (opcjonalnie)
            
        Returns:
            Krotka (jakość, url)
        """
        if preferred_quality:
            # Spróbuj znaleźć dokładne dopasowanie
            if preferred_quality in video_info.download_links:
                return preferred_quality, video_info.download_links[preferred_quality]
            
            # Spróbuj znaleźć częściowe dopasowanie
            for quality in video_info.download_links:
                if preferred_quality in quality:
                    return quality, video_info.download_links[quality]
        
        # Jeśli nie znaleziono dopasowania, zwróć najlepszą dostępną jakość
        return video_info.get_best_quality()
    
    def _download_file(
        self, 
        url: str, 
        filepath: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """
        Pobiera plik z podanego URL.
        
        Args:
            url: URL pliku
            filepath: Ścieżka do zapisu pliku
            progress_callback: Callback do aktualizacji postępu (opcjonalnie)
            
        Raises:
            DownloadError: Gdy wystąpił błąd podczas pobierania
            FileError: Gdy wystąpił błąd podczas zapisywania pliku
        """
        try:
            # Pobierz plik z obsługą strumieniowania
            response = self.session.get(url, stream=True)
            response.raise_for_status()
            
            # Pobierz rozmiar pliku
            total_size = int(response.headers.get('content-length', 0))
            
            # Utwórz pasek postępu
            progress_bar = tqdm(
                desc=filepath.name,
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            )
            
            # Zapisz plik
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=config.chunk_size):
                    if chunk:
                        size = f.write(chunk)
                        downloaded += size
                        progress_bar.update(size)
                        
                        # Wywołaj callback z postępem
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            progress_bar.close()
            
        except requests.RequestException as e:
            raise DownloadError(f"Błąd podczas pobierania pliku: {str(e)}")
        except IOError as e:
            raise FileError(f"Błąd podczas zapisywania pliku: {str(e)}")
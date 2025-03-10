"""
Moduł odpowiedzialny za pobieranie informacji o wideo z CDA.
"""
import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

from ..config import config
from ..utils import CDADownloaderException, AuthenticationError, VideoInfoError
from ..utils.helpers import extract_json_from_script, sort_qualities


@dataclass
class VideoInfo:
    """Klasa reprezentująca informacje o wideo."""
    title: str
    video_id: str
    download_links: Dict[str, str]
    thumbnail: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    duration: Optional[str] = None
    views: Optional[int] = None
    
    def get_best_quality(self) -> Tuple[str, str]:
        """
        Zwraca najlepszą dostępną jakość.
        
        Returns:
            Krotka (jakość, url)
        """
        if not self.download_links:
            raise VideoInfoError("Brak dostępnych linków do pobrania")
            
        # Sortuj jakości od najwyższej do najniższej
        sorted_qualities = sort_qualities(list(self.download_links.keys()))
        
        if not sorted_qualities:
            raise VideoInfoError("Nie można określić najlepszej jakości")
            
        best_quality = sorted_qualities[0]
        return best_quality, self.download_links[best_quality]
    
    def get_download_link(self, preferred_quality: Optional[str] = None) -> Tuple[str, str]:
        """
        Zwraca link do pobrania w określonej jakości lub najlepszej dostępnej.
        
        Args:
            preferred_quality: Preferowana jakość (opcjonalnie)
            
        Returns:
            Krotka (jakość, url)
        """
        if not self.download_links:
            raise VideoInfoError("Brak dostępnych linków do pobrania")
            
        # Jeśli podano preferowaną jakość i jest dostępna
        if preferred_quality and preferred_quality in self.download_links:
            return preferred_quality, self.download_links[preferred_quality]
            
        # W przeciwnym razie zwróć najlepszą dostępną jakość
        return self.get_best_quality()


class VideoInfoService:
    """Klasa odpowiedzialna za pobieranie informacji o wideo."""
    
    def __init__(self, session: requests.Session):
        """
        Inicjalizacja serwisu.
        
        Args:
            session: Sesja HTTP (zalogowana)
        """
        self.session = session
    
    def extract_video_id_from_url(self, url: str) -> str:
        """
        Wyodrębnia ID wideo z URL.
        
        Args:
            url: URL wideo
            
        Returns:
            ID wideo
            
        Raises:
            VideoInfoError: Gdy nie można wyodrębnić ID wideo
        """
        # Sprawdź różne formaty URL CDA
        patterns = [
            r'cda\.pl/video/(\w+)',  # https://www.cda.pl/video/1234567ab
            r'cda\.pl/(\w+)/(\w+)',  # https://www.cda.pl/user/video_id
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                # Dla pierwszego wzorca grupa to ID wideo
                if len(match.groups()) == 1:
                    return match.group(1)
                # Dla drugiego wzorca druga grupa to ID wideo
                else:
                    return match.group(2)
        
        raise VideoInfoError(f"Nie można wyodrębnić ID wideo z URL: {url}")
    
    def get_video_info(self, video_url: str) -> VideoInfo:
        """
        Pobiera informacje o wideo.
        
        Args:
            video_url: URL wideo
            
        Returns:
            Obiekt VideoInfo
            
        Raises:
            VideoInfoError: Gdy wystąpił błąd podczas pobierania informacji
            AuthenticationError: Gdy użytkownik nie jest zalogowany
        """
        try:
            logging.info(f"Pobieranie informacji o wideo: {video_url}")
            
            # Pobierz stronę wideo
            response = self.session.get(video_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Sprawdź, czy film jest premium i czy użytkownik jest zalogowany
            premium_info = soup.select_one('.premium-info')
            if premium_info and "zaloguj" in premium_info.text.lower():
                raise AuthenticationError("Musisz być zalogowany, aby uzyskać informacje o tym wideo premium")
            
            # Próbuj pobrać ID wideo z URL
            video_id = self.extract_video_id_from_url(video_url)
            
            # Pobierz tytuł filmu
            title_element = soup.select_one('h1.title')
            title = title_element.text.strip() if title_element else "film_bez_tytulu"
            
            # Pobierz link do miniatury (jeśli dostępny)
            thumbnail = None
            og_image = soup.find('meta', {'property': 'og:image'})
            if og_image:
                thumbnail = og_image.get('content')
            
            # Pobierz opis (jeśli dostępny)
            description = None
            description_element = soup.select_one('.description')
            if description_element:
                description = description_element.text.strip()
            
            # Pobierz autora (jeśli dostępny)
            author = None
            author_element = soup.select_one('.user-name')
            if author_element:
                author = author_element.text.strip()
            
            # Pobierz czas trwania (jeśli dostępny)
            duration = None
            duration_element = soup.select_one('.duration')
            if duration_element:
                duration = duration_element.text.strip()
            
            # Pobierz liczbę wyświetleń (jeśli dostępna)
            views = None
            views_element = soup.select_one('.views')
            if views_element:
                views_text = views_element.text.strip()
                views_match = re.search(r'(\d+(?:\s*\d+)*)', views_text)
                if views_match:
                    views = int(views_match.group(1).replace(" ", ""))
            
            # Pobierz linki do pobrania
            download_links = self._extract_download_links(soup)
            
            if not download_links:
                raise VideoInfoError("Nie znaleziono linków do pobrania. Film może nie być dostępny dla konta premium lub jest chroniony.")
            
            return VideoInfo(
                title=title,
                video_id=video_id,
                download_links=download_links,
                thumbnail=thumbnail,
                description=description,
                author=author,
                duration=duration,
                views=views
            )
            
        except requests.RequestException as e:
            raise VideoInfoError(f"Błąd podczas pobierania informacji o wideo: {str(e)}")
        except (json.JSONDecodeError, AttributeError) as e:
            raise VideoInfoError(f"Błąd przetwarzania danych wideo: {str(e)}")
    
    def _extract_download_links(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Wyodrębnia linki do pobrania ze strony wideo.
        
        Args:
            soup: Obiekt BeautifulSoup strony wideo
            
        Returns:
            Słownik {jakość: url}
        """
        download_links = {}
        
        # Metoda 1: Pobierz linki z danych player_data w skrypcie JS
        script_tags = soup.find_all('script')
        for script in script_tags:
            script_content = script.string
            if script_content and 'player_data' in script_content:
                try:
                    player_data_str = extract_json_from_script(script_content, 'player_data')
                    if player_data_str:
                        player_data = json.loads(player_data_str)
                        if 'video' in player_data and 'qualities' in player_data['video']:
                            for quality, data in player_data['video']['qualities'].items():
                                if 'url' in data:
                                    download_links[quality] = data['url']
                except Exception as e:
                    logging.error(f"Błąd podczas przetwarzania skryptu player_data: {e}")
        
        # Metoda 2: Jeśli nie znaleziono linków w skrypcie, spróbuj znaleźć przycisk pobierania
        if not download_links:
            download_button = soup.select_one('a.downloadBtn')
            if download_button:
                download_url = download_button.get('href')
                if download_url:
                    try:
                        # To jest tylko link do strony pobierania, nie bezpośredni link
                        response = self.session.get(download_url)
                        response.raise_for_status()
                        
                        download_soup = BeautifulSoup(response.text, 'html.parser')
                        quality_links = download_soup.select('a.quality-btn')
                        
                        for link in quality_links:
                            quality = link.text.strip()
                            url = link.get('href')
                            if url:
                                download_links[quality] = url
                    except Exception as e:
                        logging.error(f"Błąd podczas pobierania strony pobierania: {e}")
        
        return download_links
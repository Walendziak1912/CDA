"""
Moduł odpowiedzialny za wyszukiwanie wideo w serwisie CDA.
"""
import logging
from dataclasses import dataclass
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

from ..config import config
from ..utils import CDADownloaderException, SearchError, AuthenticationError


@dataclass
class SearchResult:
    """Klasa reprezentująca wynik wyszukiwania."""
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    author: Optional[str] = None
    views: Optional[str] = None
    premium: bool = False


class SearchService:
    """Klasa obsługująca wyszukiwanie wideo w serwisie CDA."""
    
    def __init__(self, session: requests.Session):
        """
        Inicjalizacja serwisu wyszukiwania.
        
        Args:
            session: Sesja HTTP (zalogowana)
        """
        self.session = session
    
    def search(self, query: str, premium_only: bool = True, page: int = 1) -> List[SearchResult]:
        """
        Wyszukuje wideo w serwisie CDA.
        
        Args:
            query: Fraza do wyszukania
            premium_only: Czy wyszukiwać tylko filmy premium
            page: Numer strony wyników
            
        Returns:
            Lista wyników wyszukiwania
            
        Raises:
            SearchError: Gdy wystąpił błąd podczas wyszukiwania
        """
        try:
            logging.info(f"Wyszukiwanie: '{query}', tylko premium: {premium_only}, strona: {page}")
            
            search_url = f"{config.base_url}/video/szukaj"
            
            params = {
                'q': query,
                'page': page,
            }
            
            if premium_only:
                params['s'] = 'premium'
            
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            results = self._parse_search_results(response.text)
            
            logging.info(f"Znaleziono {len(results)} wyników")
            return results
            
        except requests.RequestException as e:
            raise SearchError(f"Błąd podczas wyszukiwania: {str(e)}")
    
    def search_in_folder(self, folder_id: str, page: int = 1) -> List[SearchResult]:
        """
        Wyszukuje wideo w określonym folderze CDA.
        
        Args:
            folder_id: ID folderu
            page: Numer strony wyników
            
        Returns:
            Lista wyników wyszukiwania
            
        Raises:
            SearchError: Gdy wystąpił błąd podczas wyszukiwania
        """
        try:
            logging.info(f"Wyszukiwanie w folderze: {folder_id}, strona: {page}")
            
            folder_url = f"{config.base_url}/folder/{folder_id}"
            
            params = {'page': page} if page > 1 else {}
            
            response = self.session.get(folder_url, params=params)
            response.raise_for_status()
            
            results = self._parse_search_results(response.text)
            
            logging.info(f"Znaleziono {len(results)} wyników w folderze")
            return results
            
        except requests.RequestException as e:
            raise SearchError(f"Błąd podczas wyszukiwania w folderze: {str(e)}")
    
    def _parse_search_results(self, html_content: str) -> List[SearchResult]:
        """
        Parsuje wyniki wyszukiwania z HTML.
        
        Args:
            html_content: Zawartość HTML strony z wynikami
            
        Returns:
            Lista wyników wyszukiwania
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Sprawdź, czy jest wymagane logowanie
        login_required = soup.select_one('.login-premium-requied')
        if login_required:
            raise AuthenticationError("Wymagane logowanie do konta premium, aby zobaczyć wyniki wyszukiwania")
        
        # Znajdź wszystkie wyniki - video-clip-wrapper, video-clip, video-cover lub inne klasy
        video_elements = soup.select('div.video-clip-wrapper, div.video-clip, div.video-cover')
        
        for element in video_elements:
            try:
                # Wyszukaj elementy w różnych formatach strony
                title_element = (
                    element.select_one('a.link-title') or 
                    element.select_one('span.title') or
                    element.select_one('div.text-container h3')
                )
                
                url_element = (
                    element.select_one('a.link-title') or
                    element.select_one('a.thumbnail') or
                    element.select_one('a.link')
                )
                
                # Jeśli znaleziono zarówno tytuł jak i URL
                if title_element and url_element:
                    title = title_element.text.strip()
                    url = url_element.get('href')
                    
                    # Upewnij się, że URL jest pełny
                    if url and not url.startswith('http'):
                        url = f"{config.base_url}{url}"
                    
                    # Sprawdź, czy film jest premium
                    premium = False
                    premium_element = element.select_one('.premium-icon, .label-premium')
                    if premium_element:
                        premium = True
                    
                    # Pobierz miniaturę (jeśli dostępna)
                    thumbnail = None
                    img_element = element.select_one('img')
                    if img_element:
                        thumbnail = img_element.get('src') or img_element.get('data-src')
                    
                    # Pobierz czas trwania (jeśli dostępny)
                    duration = None
                    duration_element = element.select_one('.duration')
                    if duration_element:
                        duration = duration_element.text.strip()
                    
                    # Pobierz autora (jeśli dostępny)
                    author = None
                    author_element = element.select_one('.user-name')
                    if author_element:
                        author = author_element.text.strip()
                    
                    # Pobierz liczbę wyświetleń (jeśli dostępna)
                    views = None
                    views_element = element.select_one('.views')
                    if views_element:
                        views = views_element.text.strip()
                    
                    result = SearchResult(
                        title=title,
                        url=url,
                        thumbnail=thumbnail,
                        duration=duration,
                        author=author,
                        views=views,
                        premium=premium
                    )
                    
                    results.append(result)
            except Exception as e:
                logging.error(f"Błąd podczas parsowania elementu wideo: {e}")
        
        return results
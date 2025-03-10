"""
Moduł odpowiedzialny za uwierzytelnianie w serwisie CDA.
"""
import logging
import re
from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup

from ..config import config
from ..utils import CDADownloaderException, AuthenticationError, TokenError


class AuthService:
    """Klasa obsługująca uwierzytelnianie w serwisie CDA."""
    
    def __init__(self, session: Optional[requests.Session] = None):
        """
        Inicjalizacja serwisu uwierzytelniania.
        
        Args:
            session: Istniejąca sesja HTTP (opcjonalnie)
        """
        self.session = session or requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Referer': 'https://www.cda.pl/',
            'Origin': 'https://www.cda.pl'
        })
        self.session.headers.update(config.headers)
        self.logged_in = False
        self.username = None
        
    def get_csrf_token(self) -> str:
        """
        Pobiera token CSRF ze strony logowania.
        
        Returns:
            Token CSRF
            
        Raises:
            TokenError: Gdy nie udało się pobrać tokenu CSRF
        """
        try:
            logging.debug("Pobieranie tokenu CSRF ze strony logowania")
            login_page = self.session.get(config.login_url)
            login_page.raise_for_status()
            
            soup = BeautifulSoup(login_page.text, 'html.parser')
            
            # Spróbuj różne selektory dla tokenu CSRF
            token_input = (
                soup.find('input', {'name': '_token'}) or
                soup.find('input', {'name': 'csrf_token'}) or
                soup.find('input', {'name': 'token'}) or
                soup.find('meta', {'name': 'csrf-token'})
            )
            
            if token_input:
                token_value = token_input.get('value') or token_input.get('content')
                if token_value:
                    return token_value
                    
            # Alternatywna metoda - szukaj w JavaScripcie
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and ('csrf' in script.string.lower() or 'token' in script.string.lower()):
                    match = re.search(r'["\'](_token|csrf_token|token)["\']:\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        return match.group(2)
            
            # Wyświetl kod HTML strony dla debugowania
            logging.debug(f"Zawartość strony logowania: {login_page.text[:500]}...")
            
            raise TokenError("Nie udało się znaleźć tokenu CSRF na stronie logowania")
        except requests.RequestException as e:
            raise TokenError(f"Błąd podczas pobierania tokenu CSRF: {str(e)}")
    
    def login(self, username: str, password: str) -> bool:
        """
        Logowanie do serwisu CDA.
        
        Args:
            username: Nazwa użytkownika
            password: Hasło
            
        Returns:
            True jeśli logowanie powiodło się, False w przeciwnym razie
            
        Raises:
            AuthenticationError: Gdy wystąpił błąd podczas logowania
        """
        if self.logged_in:
            logging.info(f"Już zalogowano jako: {self.username}")
            return True
            
        logging.info(f"Logowanie do konta: {username}...")
        
        try:
            # Pobierz token CSRF
            csrf_token = self.get_csrf_token()
            
            # Przygotuj dane do logowania
            login_data = {
                'username': username,
                'password': password,
                '_token': csrf_token,
                'remember': '1'
            }
            
            # Wykonaj żądanie logowania
            response = self.session.post(
                config.login_url, 
                data=login_data, 
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Sprawdź, czy logowanie powiodło się
            if "premium" in response.text.lower() and username.lower() in response.text.lower():
                logging.info("Logowanie udane!")
                self.logged_in = True
                self.username = username
                return True
            else:
                logging.warning("Logowanie nieudane. Sprawdź dane logowania.")
                return False
                
        except TokenError as e:
            # Propaguj wyjątek TokenError
            raise
        except requests.RequestException as e:
            raise AuthenticationError(f"Błąd podczas logowania: {str(e)}")
    
    def logout(self) -> bool:
        """
        Wylogowanie z serwisu CDA.
        
        Returns:
            True jeśli wylogowanie powiodło się, False w przeciwnym razie
        """
        if not self.logged_in:
            logging.info("Nie jesteś zalogowany")
            return True
            
        try:
            logging.info("Wylogowywanie z konta CDA...")
            logout_url = f"{config.base_url}/logout"
            response = self.session.get(logout_url)
            response.raise_for_status()
            
            self.logged_in = False
            self.username = None
            logging.info("Wylogowano z konta CDA.")
            return True
        except requests.RequestException as e:
            logging.error(f"Błąd podczas wylogowywania: {str(e)}")
            return False
    
    def ensure_logged_in(self) -> bool:
        """
        Sprawdza, czy użytkownik jest zalogowany.
        
        Returns:
            True jeśli użytkownik jest zalogowany, False w przeciwnym razie
            
        Raises:
            AuthenticationError: Gdy użytkownik nie jest zalogowany
        """
        if not self.logged_in:
            raise AuthenticationError("Musisz być zalogowany, aby wykonać tę operację")
        return True
    
    def debug_login_page(self):
        """Zapisuje stronę logowania do pliku w celu debugowania."""
        try:
            login_page = self.session.get(config.login_url)
            with open('login_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(login_page.text)
            print("Strona logowania zapisana do pliku login_page_debug.html")
        except Exception as e:
            print(f"Błąd podczas zapisywania strony logowania: {e}")
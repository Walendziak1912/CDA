"""
Funkcje pomocnicze dla aplikacji CDA Downloader.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


def sanitize_filename(title: str) -> str:
    """
    Zamienia tytuł na bezpieczną nazwę pliku.
    
    Args:
        title: Tytuł filmu
        
    Returns:
        Bezpieczna nazwa pliku
    """
    # Usuń znaki niedozwolone w nazwach plików
    safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
    # Zamień spacje i inne białe znaki na podkreślenia
    safe_title = re.sub(r'\s+', "_", safe_title)
    # Ograniczenie długości nazwy pliku do 80 znaków
    return safe_title[:80]


def create_video_filename(title: str, quality: str, extension: str = "mp4") -> str:
    """
    Tworzy nazwę pliku dla wideo.
    
    Args:
        title: Tytuł filmu
        quality: Jakość filmu (np. '1080p')
        extension: Rozszerzenie pliku
        
    Returns:
        Pełna nazwa pliku
    """
    safe_title = sanitize_filename(title)
    return f"{safe_title}_{quality}.{extension}"


def format_file_size(size_bytes: int) -> str:
    """
    Formatuje rozmiar pliku z bajtów na czytelną wartość (KB, MB, GB).
    
    Args:
        size_bytes: Rozmiar w bajtach
        
    Returns:
        Sformatowany rozmiar pliku
    """
    # Sprawdź czy rozmiar jest nieujemny
    if size_bytes < 0:
        raise ValueError("Rozmiar pliku nie może być ujemny")
        
    # Definiowanie jednostek
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_index = 0
    
    # Konwersja do większych jednostek
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    # Zaokrąglenie do 2 miejsc po przecinku
    return f"{size:.2f} {units[unit_index]}"


def parse_quality_from_string(quality_str: str) -> int:
    """
    Parsuje wartość jakości z ciągu znaków.
    
    Args:
        quality_str: Ciąg znaków reprezentujący jakość (np. '1080p', 'HD', '720')
        
    Returns:
        Numeryczna wartość jakości lub 0 jeśli nie można rozpoznać
    """
    # Szukaj wzorca liczby w ciągu
    match = re.search(r'(\d+)', quality_str)
    if match:
        return int(match.group(1))
    
    # Mapowanie znanych jakości na wartości numeryczne
    quality_map = {
        'hd': 720,
        'fhd': 1080,
        'qhd': 1440,
        'uhd': 2160,
        '4k': 2160,
        'sd': 480,
        'ld': 360,
    }
    
    # Sprawdź, czy ciąg pasuje do któregoś z kluczy w mapie
    lower_quality = quality_str.lower()
    for key, value in quality_map.items():
        if key in lower_quality:
            return value
    
    # Nie rozpoznano jakości
    return 0


def sort_qualities(qualities: List[str]) -> List[str]:
    """
    Sortuje listę jakości od najwyższej do najniższej.
    
    Args:
        qualities: Lista ciągów znaków reprezentujących jakości
        
    Returns:
        Posortowana lista jakości
    """
    # Tworzenie listy krotek (jakość, wartość numeryczna)
    quality_values = [(q, parse_quality_from_string(q)) for q in qualities]
    
    # Sortowanie po wartości numerycznej (malejąco)
    sorted_qualities = sorted(quality_values, key=lambda x: x[1], reverse=True)
    
    # Zwracanie tylko ciągów jakości
    return [q[0] for q in sorted_qualities]


def extract_json_from_script(script_content: str, var_name: str) -> Optional[str]:
    """
    Ekstrahuje zawartość zmiennej JavaScript z ciągu znaków.
    
    Args:
        script_content: Zawartość skryptu JavaScript
        var_name: Nazwa zmiennej do wyodrębnienia
        
    Returns:
        Wyodrębniona wartość zmiennej lub None jeśli nie znaleziono
    """
    if not script_content:
        return None
        
    # Szukaj wzorca: var_name = {JSON} lub var_name={JSON}
    # Obsługuje również przypadki, gdy JSON kończy się średnikiem
    pattern = r'{0}\s*=\s*(.*?)(?:;|\s*</script>|$)'.format(var_name)
    match = re.search(pattern, script_content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return None
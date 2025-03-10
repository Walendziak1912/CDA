"""
Wyjątki dedykowane dla aplikacji CDA Downloader.
"""


class CDADownloaderException(Exception):
    """Bazowy wyjątek dla wszystkich wyjątków aplikacji."""
    pass


class AuthenticationError(CDADownloaderException):
    """Błąd uwierzytelniania."""
    pass


class TokenError(CDADownloaderException):
    """Błąd związany z tokenem CSRF."""
    pass


class VideoInfoError(CDADownloaderException):
    """Błąd pobierania informacji o wideo."""
    pass


class DownloadError(CDADownloaderException):
    """Błąd pobierania wideo."""
    pass


class SearchError(CDADownloaderException):
    """Błąd wyszukiwania."""
    pass


class FileError(CDADownloaderException):
    """Błąd zapisywania pliku."""
    pass
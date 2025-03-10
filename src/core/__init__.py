"""
Pakiet core dla aplikacji CDA Downloader.
"""

from .auth import AuthService
from .downloader import DownloaderService
from .search import SearchService, SearchResult
from .video_info import VideoInfoService, VideoInfo
from .file_manager import FileManager

__all__ = [
    'AuthService',
    'DownloaderService',
    'SearchService',
    'SearchResult',
    'VideoInfoService',
    'VideoInfo',
    'FileManager'
]
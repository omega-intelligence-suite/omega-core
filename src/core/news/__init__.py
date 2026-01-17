"""
Omega Suite - Système de monitoring crypto
Package principal contenant tous les modules
"""

__version__ = "1.0.0"
__author__ = "Antoine"

from .cryptopanic_news_ingestion import CryptoPanicNewsIngestion
from .finnhub_news_ingestion import FinnhubNewsIngestion
from .gnews_news_ingestion import GNewsNewsIngestion

__all__ = ['CryptoPanicNewsIngestion', 'GNewsNewsIngestion', 'FinnhubNewsIngestion']

"""
Omega Suite - Système de monitoring crypto
Package principal contenant tous les modules
"""

__version__ = "1.0.0"
__author__ = "Antoine"

from .ai import AI
from .telegram import Telegram

__all__ = ['AI', 'Telegram']

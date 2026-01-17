"""
Omega Suite - Système de monitoring crypto
Package principal contenant tous les modules
"""

__version__ = "1.0.0"
__author__ = "Antoine"

from .market_intelligence import MarketIntelligence
from .stocks_intelligence import StocksIntelligence
from .wallet_intelligence import WalletIntelligence
from .flash_brief import FlashBrief

__all__ = ['MarketIntelligence', 'StocksIntelligence', 'WalletIntelligence', 'FlashBrief']
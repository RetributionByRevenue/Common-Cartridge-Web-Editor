"""
Canvas Common Cartridge Generator Engine
"""

from .generator import CartridgeGenerator
from .replicator import scan_cartridge

__version__ = "1.0.0"
__all__ = ["CartridgeGenerator", "scan_cartridge"]
# BrainSAIT Healthcare Core Module
# Utility Components following OidTree 5-component pattern

from .database import DatabaseManager, get_db_connection, initialize_database
from .oid_generator import generate_oid
from .arabic_support import ArabicTextProcessor
from .config import Settings, get_settings

__all__ = [
    "DatabaseManager", "get_db_connection", "initialize_database",
    "generate_oid",
    "ArabicTextProcessor", 
    "Settings", "get_settings"
]
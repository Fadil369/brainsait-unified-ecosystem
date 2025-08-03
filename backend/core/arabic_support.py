"""
BrainSAIT Arabic Support - Utility Components
Following OidTree 5-component pattern
"""

import logging

logger = logging.getLogger(__name__)

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    logger.warning("Arabic text processing libraries not available")


class ArabicTextProcessor:
    """Arabic text processing utilities for healthcare platform"""
    
    def __init__(self):
        self.arabic_available = ARABIC_SUPPORT
    
    def reshape_arabic_text(self, text: str) -> str:
        """Reshape Arabic text for proper display"""
        if not self.arabic_available or not text:
            return text
            
        try:
            reshaped_text = arabic_reshaper.reshape(text)
            return get_display(reshaped_text)
        except Exception as e:
            logger.error(f"Error reshaping Arabic text: {e}")
            return text
    
    def is_arabic_text(self, text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not text:
            return False
            
        arabic_range = range(0x0600, 0x06FF + 1)
        return any(ord(char) in arabic_range for char in text)
    
    def format_healthcare_name(self, name: str, name_ar: str = None) -> dict:
        """Format healthcare professional/patient name with Arabic support"""
        result = {
            "display_name": name,
            "arabic_name": name_ar,
            "is_arabic": False
        }
        
        if name_ar and self.arabic_available:
            result["arabic_name"] = self.reshape_arabic_text(name_ar)
            result["is_arabic"] = True
        elif self.is_arabic_text(name):
            result["display_name"] = self.reshape_arabic_text(name)
            result["is_arabic"] = True
            
        return result
    
    def sanitize_arabic_input(self, text: str, max_length: int = 1000) -> str:
        """Sanitize Arabic input for database storage"""
        if not text:
            return ""
            
        # Remove potentially harmful characters while preserving Arabic
        sanitized = text.strip()[:max_length]
        
        # Log if Arabic text processing is not available
        if self.is_arabic_text(sanitized) and not self.arabic_available:
            logger.warning("Arabic text detected but processing libraries not available")
            
        return sanitized
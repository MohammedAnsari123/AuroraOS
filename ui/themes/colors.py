"""
AuroraOS Centralized Theme System
Defines colors and styles for system-wide themes
"""

class Theme:
    """Base theme class with color definitions"""
    
    # Theme metadata
    NAME = "Base"
    
    # Common status colors (usually consistent across themes)
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"

class AuroraTheme(Theme):
    """Original Aurora theme - Northern lights inspired"""
    NAME = "Aurora"
    
    # Main colors
    DEEP_BLACK = "#0A0E27"
    DARK_BLUE = "#1A1F3A"
    MIDNIGHT = "#151934"
    
    # Aurora colors
    NEON_BLUE = "#5E60CE"
    PURPLE = "#9D4EDD"
    TEAL = "#00D9FF"
    CYAN = "#00F5FF"
    PINK = "#FF006E"
    
    # UI colors
    BG_PRIMARY = DEEP_BLACK
    BG_SECONDARY = DARK_BLUE
    BG_TERTIARY = MIDNIGHT
    
    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B8C1EC"
    TEXT_TERTIARY = "#6B7280"
    
    ACCENT = TEAL
    ACCENT_SECONDARY = PURPLE
    
    # Shadows and glows
    GLOW_ACCENT = "#00D9FF40"

class ClassicLightTheme(Theme):
    """Classic Light theme - Professional and clean"""
    NAME = "Classic Light"
    
    # Main colors
    OFF_WHITE = "#F3F4F6"
    LIGHT_GRAY = "#E5E7EB"
    MID_GRAY = "#D1D5DB"
    
    # Accents
    BLUE_ACCENT = "#2563EB"
    DARK_BLUE = "#1E40AF"
    
    # UI colors
    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = OFF_WHITE
    BG_TERTIARY = LIGHT_GRAY
    
    TEXT_PRIMARY = "#111827"
    TEXT_SECONDARY = "#4B5563"
    TEXT_TERTIARY = "#9CA3AF"
    
    ACCENT = BLUE_ACCENT
    ACCENT_SECONDARY = DARK_BLUE
    
    # Shadows and glows
    GLOW_ACCENT = "#2563EB20"

# DEFAULT THEME
# Note: You can change this to ClassicLightTheme or AuroraTheme
CURRENT_THEME = ClassicLightTheme

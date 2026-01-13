"""
Tile classes representing different terrain types.
Uses abstract base class for extensibility.
"""

from abc import ABC, abstractmethod
from typing import Tuple
import config


class Tile(ABC):
    """
    Abstract base class for all terrain tiles.
    Enforces common interface for different terrain types.
    """
    
    def __init__(self, x: int, y: int):
        """
        Initialize a tile at grid coordinates.
        
        Args:
            x: Grid x-coordinate
            y: Grid y-coordinate
        """
        self.x = x
        self.y = y
        self.has_plant = False
    
    @abstractmethod
    def get_color(self) -> str:
        """Return the display color for this tile type."""
        pass
    
    @abstractmethod
    def can_support_plant(self) -> bool:
        """Return whether this tile can support plant life."""
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.x}, {self.y})"


class WaterTile(Tile):
    """Represents water terrain. Cannot support plants."""
    
    def get_color(self) -> str:
        return config.COLORS['water']
    
    def can_support_plant(self) -> bool:
        return False


class LandTile(Tile):
    """
    Represents land terrain with fertility-based coloring.
    Can support plants if unoccupied. Visual appearance reflects fertility.
    """
    
    def __init__(self, x: int, y: int, fertility: float = 0.5):
        """
        Initialize a land tile with fertility value.
        
        Args:
            x: Grid x-coordinate
            y: Grid y-coordinate
            fertility: Fertility value [0, 1], affects color and plant spawn rate
        """
        super().__init__(x, y)
        self.fertility = max(0.0, min(1.0, fertility))  # Clamp to [0, 1]
    
    def get_color(self) -> str:
        """
        Return color based on fertility level.
        Creates smooth gradient from tan (infertile) to dark green (fertile).
        """
        return self._interpolate_fertility_color(self.fertility)
    
    def _interpolate_fertility_color(self, fertility: float) -> str:
        """
        Interpolate between fertility color stops based on fertility value.
        
        Args:
            fertility: Fertility value [0, 1]
            
        Returns:
            Hex color string
        """
        # Define color stops (fertility_value, color_name)
        color_stops = [
            (0.0, 'infertile'),
            (0.15, 'low'),
            (0.30, 'medium_low'),
            (0.45, 'medium'),
            (0.60, 'medium_high'),
            (0.80, 'high'),
            (1.0, 'very_high'),
        ]
        
        # Find the two stops to interpolate between
        for i in range(len(color_stops) - 1):
            lower_fertility, lower_color = color_stops[i]
            upper_fertility, upper_color = color_stops[i + 1]
            
            if lower_fertility <= fertility <= upper_fertility:
                # Calculate interpolation factor
                if upper_fertility == lower_fertility:
                    t = 0
                else:
                    t = (fertility - lower_fertility) / (upper_fertility - lower_fertility)
                
                # Interpolate between the two colors
                return self._interpolate_hex_colors(
                    config.FERTILITY_COLORS[lower_color],
                    config.FERTILITY_COLORS[upper_color],
                    t
                )
        
        # Fallback (shouldn't reach here if fertility is [0, 1])
        return config.FERTILITY_COLORS['medium']
    
    def _interpolate_hex_colors(self, color1: str, color2: str, t: float) -> str:
        """
        Linearly interpolate between two hex colors.
        
        Args:
            color1: Starting hex color (e.g., '#RRGGBB')
            color2: Ending hex color
            t: Interpolation factor [0, 1]
            
        Returns:
            Interpolated hex color string
        """
        # Parse hex colors to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Interpolate each channel
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def can_support_plant(self) -> bool:
        return not self.has_plant
    
    def get_fertility(self) -> float:
        """Return the fertility value of this tile."""
        return self.fertility
"""
Strategy pattern implementation for plant spawn probability calculation.
Now uses fertility-based approach for more realistic plant distribution.
"""

from abc import ABC, abstractmethod
from typing import List
from models.tile import Tile, LandTile


class SpawnProbabilityStrategy(ABC):
    """Abstract strategy for calculating plant spawn probability."""
    
    @abstractmethod
    def calculate_probability(self, tile: Tile, grid: List[List[Tile]]) -> float:
        """
        Calculate spawn probability for a given tile.
        
        Args:
            tile: The tile to calculate probability for
            grid: The complete terrain grid for context
            
        Returns:
            Probability value between 0.0 and 1.0
        """
        pass


class FertilityBasedStrategy(SpawnProbabilityStrategy):
    """
    Calculate spawn probability based on land fertility.
    Strongly favors fertile areas near water.
    """
    
    def __init__(self, base_probability: float = 0.08, fertility_multiplier: float = 3.0):
        """
        Initialize strategy with configurable parameters.
        
        Args:
            base_probability: Base spawn probability
            fertility_multiplier: How much fertility affects spawn rate
        """
        self.base_probability = base_probability
        self.fertility_multiplier = fertility_multiplier
    
    def calculate_probability(self, tile: Tile, grid: List[List[Tile]]) -> float:
        """Calculate probability using tile's fertility value."""
        if not tile.can_support_plant():
            return 0.0
        
        if not isinstance(tile, LandTile):
            return 0.0
        
        fertility = tile.get_fertility()
        
        probability = self.base_probability * (
            1.0 + fertility * self.fertility_multiplier
        )
        
        return min(probability, 1.0)
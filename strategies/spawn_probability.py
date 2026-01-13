"""
Strategy pattern implementation for plant spawn probability calculation.
Now uses fertility-based approach for more realistic plant distribution.
"""

from abc import ABC, abstractmethod
from typing import List
from models.tile import Tile, LandTile
import config


class SpawnProbabilityStrategy(ABC):
    """
    Abstract strategy for calculating plant spawn probability.
    """
    
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
    Strongly favors fertile areas near water, creating visible vegetation patterns.
    """
    
    def calculate_probability(self, tile: Tile, grid: List[List[Tile]]) -> float:
        """
        Calculate probability using tile's fertility value.
        
        High fertility areas (near water) get significantly higher spawn rates,
        creating dense vegetation along coastlines and riverbanks.
        
        Args:
            tile: The tile to calculate probability for
            grid: The complete terrain grid (unused but kept for interface compatibility)
            
        Returns:
            Probability value between 0.0 and 1.0
        """
        if not tile.can_support_plant():
            return 0.0
        
        # Only LandTiles have fertility
        if not isinstance(tile, LandTile):
            return 0.0
        
        fertility = tile.get_fertility()
        
        # Fertility strongly amplifies spawn probability
        # Formula: base_prob * (1 + fertility * multiplier)
        # Result: fertile areas get FERTILITY_SPAWN_MULTIPLIER times more plants
        probability = config.BASE_SPAWN_PROBABILITY * (
            1.0 + fertility * config.FERTILITY_SPAWN_MULTIPLIER
        )
        
        # Clamp to valid probability range
        return min(probability, 1.0)


class WaterProximityStrategy(SpawnProbabilityStrategy):
    """
    Legacy strategy: Calculate spawn probability based on distance to nearest water.
    Kept for backward compatibility. Consider using FertilityBasedStrategy instead.
    """
    
    def calculate_probability(self, tile: Tile, grid: List[List[Tile]]) -> float:
        """
        Calculate probability with bonus for water proximity.
        
        Note: This strategy is less efficient than FertilityBasedStrategy
        because it recalculates distances every time. The fertility approach
        pre-computes distances during terrain generation.
        """
        if not tile.can_support_plant():
            return 0.0
        
        # If tile has fertility info, use it
        if isinstance(tile, LandTile):
            fertility = tile.get_fertility()
            return config.BASE_SPAWN_PROBABILITY * (
                1.0 + fertility * config.FERTILITY_SPAWN_MULTIPLIER
            )
        
        # Fallback to legacy distance calculation
        distance = self._find_nearest_water_distance(tile, grid)
        
        if distance <= config.WATER_PROXIMITY_BONUS_RANGE:
            bonus_multiplier = 1.0 + (1.0 - distance / config.WATER_PROXIMITY_BONUS_RANGE)
            return min(config.BASE_SPAWN_PROBABILITY * bonus_multiplier, 1.0)
        
        return config.BASE_SPAWN_PROBABILITY
    
    def _find_nearest_water_distance(self, tile: Tile, grid: List[List[Tile]]) -> float:
        """Find Manhattan distance to nearest water tile."""
        from models.tile import WaterTile
        
        min_distance = float('inf')
        search_range = config.WATER_PROXIMITY_BONUS_RANGE + 1
        
        for dy in range(-search_range, search_range + 1):
            for dx in range(-search_range, search_range + 1):
                x, y = tile.x + dx, tile.y + dy
                
                if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                    if isinstance(grid[y][x], WaterTile):
                        distance = abs(dx) + abs(dy)
                        min_distance = min(min_distance, distance)
                        
                        if min_distance == 1:
                            return min_distance
        
        return min_distance if min_distance != float('inf') else search_range
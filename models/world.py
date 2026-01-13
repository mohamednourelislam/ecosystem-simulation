"""
World class - central container for all simulation state.
Manages terrain, entities, and provides query interface.
"""

from typing import List, Optional, Set, Tuple
from models.tile import Tile, LandTile, WaterTile
from models.plant import Plant
import config


class World:
    """
    Contains and manages the entire simulation state.
    Provides clean interface for querying and modifying world state.
    """
    
    def __init__(self):
        """Initialize empty world."""
        self.grid: List[List[Tile]] = []
        self.plants: List[Plant] = []
        self.simulation_ticks = 0
        self._observers: List['SimulationObserver'] = []
        
    def set_terrain(self, grid: List[List[Tile]]) -> None:
        """
        Set the terrain grid for this world.
        
        Args:
            grid: 2D list of Tile objects
        """
        self.grid = grid
        self._notify_observers()
        
    def add_plant(self, plant: Plant) -> bool:
        """
        Add a plant to the world if constraints allow.
        
        Args:
            plant: Plant instance to add
            
        Returns:
            True if plant was added, False otherwise
        """
        if len(self.plants) >= config.MAX_PLANTS:
            return False
        
        tile = self.get_tile(plant.x, plant.y)
        if tile and tile.can_support_plant():
            self.plants.append(plant)
            tile.has_plant = True
            self._notify_observers()
            return True
        
        return False
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """
        Get tile at specified grid coordinates.
        
        Args:
            x: Grid x-coordinate
            y: Grid y-coordinate
            
        Returns:
            Tile at position or None if out of bounds
        """
        if 0 <= x < len(self.grid[0]) and 0 <= y < len(self.grid):
            return self.grid[y][x]
        return None
    
    def update(self) -> None:
        """
        Update world state by one simulation tick.
        Updates all plants and increments tick counter.
        """
        for plant in self.plants:
            plant.update()
        
        self.simulation_ticks += 1
        self._notify_observers()
        
    def get_statistics(self) -> dict:
        """
        Get current world statistics.
        
        Returns:
            Dictionary containing current statistics
        """
        land_count = sum(
            1 for row in self.grid 
            for tile in row 
            if isinstance(tile, LandTile)
        )
        water_count = sum(
            1 for row in self.grid 
            for tile in row 
            if isinstance(tile, WaterTile)
        )
        
        return {
            'land_tiles': land_count,
            'water_tiles': water_count,
            'plant_count': len(self.plants),
            'max_plants': config.MAX_PLANTS,
            'simulation_ticks': self.simulation_ticks
        }
        
    def attach_observer(self, observer: 'SimulationObserver') -> None:
        """Attach an observer to receive state change notifications."""
        self._observers.append(observer)
    
    def _notify_observers(self) -> None:
        """Notify all observers of state change."""
        for observer in self._observers:
            observer.on_world_changed(self)
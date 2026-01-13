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
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get world statistics."""
        if not self.terrain:
            return {
                'plant_count': 0,
                'land_tiles': 0,
                'water_tiles': 0,
                'avg_fertility': 0.0
            }

        land_count = sum(1 for tile in self.terrain.tiles.values() 
                         if tile.terrain_type == TerrainType.LAND)
        water_count = len(self.terrain.tiles) - land_count

        avg_fertility = sum(tile.fertility for tile in self.terrain.tiles.values() 
                           if tile.terrain_type == TerrainType.LAND) / max(land_count, 1)

        return {
            'plant_count': len(self.plants),
            'land_tiles': land_count,
            'water_tiles': water_count,
            'avg_fertility': avg_fertility
        }
        
    def attach_observer(self, observer: 'SimulationObserver') -> None:
        """Attach an observer to receive state change notifications."""
        self._observers.append(observer)
        
    def clear(self) -> None:
        """Clear all world state."""
        self.plants.clear()
        self.terrain = None
        self._notify_observers()
    
    def _notify_observers(self) -> None:
        """Notify all observers of state change."""
        for observer in self._observers:
            observer.on_world_changed(self)
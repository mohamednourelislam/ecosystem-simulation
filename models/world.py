"""
World class - central container for all simulation state.
Manages terrain, plants, creatures, and provides query interface.
"""

from typing import List, Optional, Dict, Any
from models.tile import Tile, LandTile, WaterTile
from models.plant import Plant


class World:
    """
    Contains and manages the entire simulation state.
    Provides clean interface for querying and modifying world state.
    """
    
    def __init__(self, max_plants: int = 200, max_creatures: int = 50):
        """Initialize empty world."""
        self.grid: List[List[Tile]] = []
        self.plants: List[Plant] = []
        self.creatures: List = []  # List of Creature objects
        self.simulation_ticks = 0
        self.max_plants = max_plants
        self.max_creatures = max_creatures
        
    def set_terrain(self, grid: List[List[Tile]]) -> None:
        """Set the terrain grid for this world."""
        self.grid = grid
        
    def add_plant(self, plant: Plant) -> bool:
        """Add a plant to the world if constraints allow."""
        if len(self.plants) >= self.max_plants:
            return False
        
        tile = self.get_tile(plant.x, plant.y)
        if tile and tile.can_support_plant():
            self.plants.append(plant)
            tile.has_plant = True
            return True
        
        return False
    
    def remove_plant(self, plant: Plant) -> bool:
        """
        Remove a plant from the world (e.g., when eaten).
        
        Args:
            plant: Plant to remove
            
        Returns:
            True if plant was removed
        """
        if plant in self.plants:
            tile = self.get_tile(plant.x, plant.y)
            if tile:
                tile.has_plant = False
            self.plants.remove(plant)
            return True
        return False
    
    def add_creature(self, creature) -> bool:
        """
        Add a creature to the world if constraints allow.
        
        Args:
            creature: Creature to add
            
        Returns:
            True if creature was added
        """
        if len(self.creatures) >= self.max_creatures:
            return False
        
        self.creatures.append(creature)
        return True
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at specified grid coordinates."""
        if self.grid and 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
            return self.grid[y][x]
        return None
    
    def update(self) -> None:
        """Update world state by one simulation tick."""
        for plant in self.plants:
            plant.update()
        
        # Creatures are updated by CreatureManager
        
        self.simulation_ticks += 1
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get world statistics."""
        if not self.grid:
            return {
                'plant_count': 0,
                'creature_count': 0,
                'male_count': 0,
                'female_count': 0,
                'newborn_count': 0,
                'adult_count': 0,
                'land_tiles': 0,
                'water_tiles': 0,
                'avg_fertility': 0.0,
                'max_plants': self.max_plants,
                'max_creatures': self.max_creatures
            }

        land_tiles = []
        water_count = 0
        
        for row in self.grid:
            for tile in row:
                if isinstance(tile, WaterTile):
                    water_count += 1
                elif isinstance(tile, LandTile):
                    land_tiles.append(tile)

        land_count = len(land_tiles)
        avg_fertility = sum(tile.get_fertility() for tile in land_tiles) / max(land_count, 1)

        # Import here to avoid circular dependency
        from models.creature import Gender, LifeStage
        
        alive_creatures = [c for c in self.creatures if c.is_alive]
        male_count = sum(1 for c in alive_creatures if c.gender == Gender.MALE)
        female_count = sum(1 for c in alive_creatures if c.gender == Gender.FEMALE)
        newborn_count = sum(1 for c in alive_creatures if c.life_stage == LifeStage.NEWBORN)
        adult_count = sum(1 for c in alive_creatures if c.life_stage == LifeStage.ADULT)

        return {
            'plant_count': len(self.plants),
            'creature_count': len(alive_creatures),
            'male_count': male_count,
            'female_count': female_count,
            'newborn_count': newborn_count,
            'adult_count': adult_count,
            'land_tiles': land_count,
            'water_tiles': water_count,
            'avg_fertility': avg_fertility,
            'max_plants': self.max_plants,
            'max_creatures': self.max_creatures
        }
        
    def clear(self) -> None:
        """Clear all world state."""
        for row in self.grid:
            for tile in row:
                tile.has_plant = False
        
        self.plants.clear()
        self.creatures.clear()
        self.grid = []
        self.simulation_ticks = 0
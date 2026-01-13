"""
Plant spawning service - manages plant creation logic.
Uses strategy pattern for probability calculation.
"""

import random
from typing import List
from models.world import World
from models.plant import Plant
from models.tile import Tile
from strategies.spawn_probability import SpawnProbabilityStrategy


class PlantSpawner:
    """
    Service responsible for spawning plants in the world.
    Decoupled from rendering and uses injected strategy for probability.
    """
    
    def __init__(self, strategy: SpawnProbabilityStrategy):
        """
        Initialize spawner with probability strategy.
        
        Args:
            strategy: Strategy for calculating spawn probability
        """
        self.strategy = strategy
        
    def attempt_spawn(self, world: World) -> bool:
        """
        Attempt to spawn a plant somewhere in the world.
        
        Uses strategy to weight spawn probability by location.
        Only attempts spawn if under max plant capacity.
        
        Args:
            world: The world to spawn plant in
            
        Returns:
            True if a plant was spawned, False otherwise
        """
        # Check capacity
        stats = world.get_statistics()
        if stats['plant_count'] >= stats['max_plants']:
            return False
        
        # Collect eligible tiles with probabilities
        eligible_tiles = []
        probabilities = []
        
        for row in world.grid:
            for tile in row:
                if tile.can_support_plant():
                    prob = self.strategy.calculate_probability(tile, world.grid)
                    if prob > 0:
                        eligible_tiles.append(tile)
                        probabilities.append(prob)
        
        if not eligible_tiles:
            return False
        
        # Weighted random selection
        total_prob = sum(probabilities)
        normalized_probs = [p / total_prob for p in probabilities]
        
        selected_tile = random.choices(eligible_tiles, weights=normalized_probs, k=1)[0]
        
        # Create and add plant
        plant = Plant(selected_tile.x, selected_tile.y)
        return world.add_plant(plant)
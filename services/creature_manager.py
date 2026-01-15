"""
Creature manager - handles creature AI, movement, and reproduction.
"""

import random
from typing import List, Optional, Tuple
from models.creature import Creature, Gender, LifeStage
from models.world import World
from models.plant import Plant
import config


class CreatureManager:
    """
    Manages all creature behaviors including:
    - Movement towards food or mates
    - Eating plants
    - Reproduction
    - Birth and death
    """
    
    def __init__(self):
        """Initialize creature manager."""
        self.search_radius = 15  # How far creatures can see
    
    def update_creatures(self, world: World) -> None:
        """
        Update all creatures in the world.
        
        Args:
            world: The world containing creatures
        """
        # Remove dead creatures
        world.creatures = [c for c in world.creatures if c.is_alive]
        
        # Update each creature
        for creature in world.creatures:
            creature.update()
            
            if not creature.is_alive:
                continue
            
            # Behavior priority:
            # 1. If hungry and can see food -> move to and eat food
            # 2. If can reproduce -> find mate
            # 3. Otherwise -> wander randomly
            
            if creature.energy < creature.MAX_ENERGY * 0.7:  # Hungry
                self._seek_and_eat_food(creature, world)
            elif creature.can_reproduce():
                self._seek_mate_and_reproduce(creature, world)
            else:
                # Random movement
                creature.move_random(config.GRID_WIDTH, config.GRID_HEIGHT)
        
        # Handle reproduction (after all updates to avoid modifying list during iteration)
        self._process_reproductions(world)
    
    def _seek_and_eat_food(self, creature: Creature, world: World) -> None:
        """
        Make creature seek nearby plants and eat them.
        
        Args:
            creature: The creature seeking food
            world: The world containing plants
        """
        # First check if there's a plant at current position
        plant_at_pos = self._find_plant_at_position(creature.x, creature.y, world.plants)
        if plant_at_pos:
            world.remove_plant(plant_at_pos)
            creature.eat_plant()
            return
        
        # Find nearest plant within search radius
        nearest_plant = self._find_nearest_plant(creature, world.plants)
        
        if nearest_plant:
            # Move towards plant
            creature.move_towards(
                nearest_plant.x,
                nearest_plant.y,
                config.GRID_WIDTH,
                config.GRID_HEIGHT
            )
            
            # Check if reached plant after moving
            if creature.x == nearest_plant.x and creature.y == nearest_plant.y:
                world.remove_plant(nearest_plant)
                creature.eat_plant()
        else:
            # No food nearby, move randomly
            creature.move_random(config.GRID_WIDTH, config.GRID_HEIGHT)
    
    def _seek_mate_and_reproduce(self, creature: Creature, world: World) -> None:
        """
        Make creature seek potential mates and reproduce.
        
        Args:
            creature: The creature seeking a mate
            world: The world containing other creatures
        """
        # Find nearby opposite gender adults
        potential_mates = [
            c for c in world.creatures
            if c.is_alive
            and c != creature
            and c.gender != creature.gender
            and c.can_reproduce()
        ]
        
        if not potential_mates:
            creature.move_random(config.GRID_WIDTH, config.GRID_HEIGHT)
            return
        
        # Find nearest mate
        nearest_mate = min(
            potential_mates,
            key=lambda c: abs(c.x - creature.x) + abs(c.y - creature.y)
        )
        
        distance = abs(creature.x - nearest_mate.x) + abs(creature.y - nearest_mate.y)
        
        if distance <= Creature.REPRODUCTION_RANGE:
            # Close enough to reproduce - mark for reproduction
            if not hasattr(creature, '_reproduction_partner'):
                creature._reproduction_partner = nearest_mate
        else:
            # Move towards mate
            creature.move_towards(
                nearest_mate.x,
                nearest_mate.y,
                config.GRID_WIDTH,
                config.GRID_HEIGHT
            )
    
    def _process_reproductions(self, world: World) -> None:
        """
        Process all pending reproductions and create offspring.
        
        Args:
            world: The world to add offspring to
        """
        processed_pairs = set()
        
        for creature in world.creatures:
            if not hasattr(creature, '_reproduction_partner'):
                continue
            
            partner = creature._reproduction_partner
            
            # Create unique pair ID (sorted to avoid duplicates)
            pair_id = tuple(sorted([id(creature), id(partner)]))
            
            if pair_id in processed_pairs:
                continue
            
            # Verify both can still reproduce
            if creature.reproduce_with(partner):
                # Create offspring
                num_offspring = random.randint(1, 3)  # 1-3 babies
                
                for _ in range(num_offspring):
                    # Baby spawns near parents
                    baby_x = (creature.x + partner.x) // 2 + random.randint(-1, 1)
                    baby_y = (creature.y + partner.y) // 2 + random.randint(-1, 1)
                    
                    # Clamp to bounds
                    baby_x = max(0, min(baby_x, config.GRID_WIDTH - 1))
                    baby_y = max(0, min(baby_y, config.GRID_HEIGHT - 1))
                    
                    # Random gender
                    baby_gender = random.choice([Gender.MALE, Gender.FEMALE])
                    
                    baby = Creature(baby_x, baby_y, baby_gender, LifeStage.NEWBORN)
                    world.add_creature(baby)
                
                # Consume resources
                creature.consume_reproduction_resources()
                partner.consume_reproduction_resources()
                
                processed_pairs.add(pair_id)
            
            # Clean up partner reference
            delattr(creature, '_reproduction_partner')
    
    def _find_nearest_plant(self, creature: Creature, plants: List[Plant]) -> Optional[Plant]:
        """
        Find the nearest plant within search radius.
        
        Args:
            creature: The creature searching for food
            plants: List of all plants in world
            
        Returns:
            Nearest plant or None
        """
        nearby_plants = [
            plant for plant in plants
            if abs(plant.x - creature.x) <= self.search_radius
            and abs(plant.y - creature.y) <= self.search_radius
        ]
        
        if not nearby_plants:
            return None
        
        return min(
            nearby_plants,
            key=lambda p: abs(p.x - creature.x) + abs(p.y - creature.y)
        )
    
    def _find_plant_at_position(self, x: int, y: int, plants: List[Plant]) -> Optional[Plant]:
        """
        Find plant at exact position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            plants: List of all plants
            
        Returns:
            Plant at position or None
        """
        for plant in plants:
            if plant.x == x and plant.y == y:
                return plant
        return None
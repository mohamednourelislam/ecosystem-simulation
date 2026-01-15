"""
Creature entity representing animals in the ecosystem.
Includes movement, eating, reproduction, and lifecycle.
"""

from typing import Tuple, Optional
from enum import Enum
import random


class Gender(Enum):
    """Creature gender for reproduction."""
    MALE = "male"
    FEMALE = "female"


class LifeStage(Enum):
    """Creature life stages."""
    NEWBORN = "newborn"
    ADULT = "adult"


class Creature:
    """
    Represents an animal in the simulation.
    Can move, eat plants, reproduce, and grow from newborn to adult.
    """
    
    # Class constants
    PLANTS_TO_GROW = 5          # Plants needed for newborn to become adult
    PLANTS_TO_REPRODUCE = 10    # Plants adult needs to reproduce
    REPRODUCTION_RANGE = 3      # Max distance to find mate
    MAX_AGE = 1000              # Max age before natural death
    MOVEMENT_SPEED = 1          # Tiles per move
    ENERGY_LOSS_PER_TICK = 0.5  # Energy lost each update
    ENERGY_FROM_PLANT = 20      # Energy gained from eating a plant
    MAX_ENERGY = 100            # Maximum energy
    STARVATION_THRESHOLD = 0    # Dies if energy reaches this
    
    def __init__(self, x: int, y: int, gender: Gender, life_stage: LifeStage = LifeStage.NEWBORN):
        """
        Initialize a creature.
        
        Args:
            x: Grid x-coordinate
            y: Grid y-coordinate
            gender: MALE or FEMALE
            life_stage: NEWBORN or ADULT
        """
        self.x = x
        self.y = y
        self.gender = gender
        self.life_stage = life_stage
        
        # Stats
        self.age = 0
        self.plants_eaten = 0
        self.energy = 50.0  # Start with half energy
        self.is_alive = True
        self.offspring_count = 0
        
        # Reproduction cooldown
        self.reproduction_cooldown = 0
        self.reproduction_cooldown_max = 50  # Ticks between reproductions
    
    def update(self) -> None:
        """Update creature state each tick."""
        if not self.is_alive:
            return
        
        self.age += 1
        self.energy -= self.ENERGY_LOSS_PER_TICK
        
        # Check for death conditions
        if self.energy <= self.STARVATION_THRESHOLD:
            self.is_alive = False
            return
        
        if self.age >= self.MAX_AGE:
            self.is_alive = False
            return
        
        # Check for growth
        if self.life_stage == LifeStage.NEWBORN and self.plants_eaten >= self.PLANTS_TO_GROW:
            self.life_stage = LifeStage.ADULT
        
        # Update reproduction cooldown
        if self.reproduction_cooldown > 0:
            self.reproduction_cooldown -= 1
    
    def eat_plant(self) -> None:
        """Eat a plant, gaining energy and progress toward growth/reproduction."""
        self.plants_eaten += 1
        self.energy = min(self.energy + self.ENERGY_FROM_PLANT, self.MAX_ENERGY)
    
    def can_reproduce(self) -> bool:
        """Check if this creature can reproduce."""
        return (
            self.is_alive and
            self.life_stage == LifeStage.ADULT and
            self.plants_eaten >= self.PLANTS_TO_REPRODUCE and
            self.reproduction_cooldown == 0
        )
    
    def reproduce_with(self, partner: 'Creature') -> bool:
        """
        Attempt reproduction with a partner.
        
        Args:
            partner: Another creature to reproduce with
            
        Returns:
            True if reproduction is possible
        """
        if not self.can_reproduce() or not partner.can_reproduce():
            return False
        
        if self.gender == partner.gender:
            return False
        
        # Check distance
        distance = abs(self.x - partner.x) + abs(self.y - partner.y)
        if distance > self.REPRODUCTION_RANGE:
            return False
        
        return True
    
    def consume_reproduction_resources(self) -> None:
        """Consume resources used in reproduction."""
        self.plants_eaten = max(0, self.plants_eaten - self.PLANTS_TO_REPRODUCE)
        self.reproduction_cooldown = self.reproduction_cooldown_max
        self.offspring_count += 1
    
    def move_towards(self, target_x: int, target_y: int, grid_width: int, grid_height: int) -> None:
        """
        Move one step towards a target position.
        
        Args:
            target_x: Target x-coordinate
            target_y: Target y-coordinate
            grid_width: Maximum x boundary
            grid_height: Maximum y boundary
        """
        if not self.is_alive:
            return
        
        # Calculate direction
        dx = 0 if target_x == self.x else (1 if target_x > self.x else -1)
        dy = 0 if target_y == self.y else (1 if target_y > self.y else -1)
        
        # Move
        new_x = self.x + dx * self.MOVEMENT_SPEED
        new_y = self.y + dy * self.MOVEMENT_SPEED
        
        # Clamp to grid bounds
        self.x = max(0, min(new_x, grid_width - 1))
        self.y = max(0, min(new_y, grid_height - 1))
    
    def move_random(self, grid_width: int, grid_height: int) -> None:
        """
        Move randomly (when no specific target).
        
        Args:
            grid_width: Maximum x boundary
            grid_height: Maximum y boundary
        """
        if not self.is_alive:
            return
        
        dx = random.choice([-1, 0, 1]) * self.MOVEMENT_SPEED
        dy = random.choice([-1, 0, 1]) * self.MOVEMENT_SPEED
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Clamp to grid bounds
        self.x = max(0, min(new_x, grid_width - 1))
        self.y = max(0, min(new_y, grid_height - 1))
    
    def get_position(self) -> Tuple[int, int]:
        """Return the grid position of this creature."""
        return (self.x, self.y)
    
    def get_color(self) -> str:
        """Return display color based on gender and life stage."""
        if self.life_stage == LifeStage.NEWBORN:
            return '#FFD700' if self.gender == Gender.MALE else '#FFA500'
        else:
            return '#0000FF' if self.gender == Gender.MALE else '#FF1493'
    
    def get_size(self) -> float:
        """Return display size multiplier based on life stage."""
        return 0.5 if self.life_stage == LifeStage.NEWBORN else 1.0
    
    def __repr__(self) -> str:
        return (f"Creature({self.gender.value}, {self.life_stage.value}, "
                f"pos=({self.x},{self.y}), age={self.age}, plants={self.plants_eaten})")
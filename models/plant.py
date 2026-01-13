"""
Plant entity representing vegetation in the ecosystem.
"""

from typing import Tuple


class Plant:
    """
    Represents a plant entity in the simulation.
    Currently static, but designed for future growth/lifecycle features.
    """
    
    def __init__(self, x: int, y: int):
        """
        Initialize a plant at grid coordinates.
        
        Args:
            x: Grid x-coordinate
            y: Grid y-coordinate
        """
        self.x = x
        self.y = y
        self.age = 0  # Placeholder for future lifecycle features
        self.health = 100  # Placeholder for future health system
        
    def update(self) -> None:
        """
        Update plant state (currently just increments age).
        Placeholder for future growth, reproduction, death logic.
        """
        self.age += 1
    
    def get_position(self) -> Tuple[int, int]:
        """Return the grid position of this plant."""
        return (self.x, self.y)
    
    def __repr__(self) -> str:
        return f"Plant({self.x}, {self.y}, age={self.age})"
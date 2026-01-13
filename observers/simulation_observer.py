"""
Observer pattern implementation for decoupled UI updates.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.world import World


class SimulationObserver(ABC):
    """
    Abstract observer for simulation state changes.
    Allows UI components to react without tight coupling.
    """
    
    @abstractmethod
    def on_world_changed(self, world: 'World') -> None:
        """
        Called when world state changes.
        
        Args:
            world: The world that changed
        """
        pass
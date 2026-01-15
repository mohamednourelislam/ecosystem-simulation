"""
Renderer - handles all drawing to the Tkinter canvas.
"""

import tkinter as tk
from typing import List
from models.tile import Tile
from models.plant import Plant
import config


class Renderer:
    """
    Responsible for rendering the simulation state to canvas.
    """
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.tile_rectangles = {}
        self.plant_ovals = {}
        self.creature_ovals = {}
        
    def render_initial_blank(self) -> None:
        """Render blank initial state."""
        self.canvas.delete('all')
        self.canvas.create_text(
            config.CANVAS_WIDTH // 2,
            config.CANVAS_HEIGHT // 2,
            text="Configure parameters and click Start",
            font=('Arial', 16),
            fill='#999999'
        )
        
    def render_terrain(self, grid: List[List[Tile]]) -> None:
        """Render the terrain grid."""
        for y, row in enumerate(grid):
            for x, tile in enumerate(row):
                x1 = x * config.TILE_SIZE
                y1 = y * config.TILE_SIZE
                x2 = x1 + config.TILE_SIZE
                y2 = y1 + config.TILE_SIZE
                
                rect_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=tile.get_color(),
                    outline=''
                )
                self.tile_rectangles[(x, y)] = rect_id
                
    def render_plants(self, plants: List[Plant]) -> None:
        """Render all plants."""
        # Clear old plants
        for oval_id in self.plant_ovals.values():
            self.canvas.delete(oval_id)
        self.plant_ovals.clear()
        
        # Draw current plants
        for plant in plants:
            x1 = plant.x * config.TILE_SIZE + 1
            y1 = plant.y * config.TILE_SIZE + 1
            x2 = (plant.x + 1) * config.TILE_SIZE - 1
            y2 = (plant.y + 1) * config.TILE_SIZE - 1
            
            oval_id = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=config.COLORS['plant'],
                outline=''
            )
            self.plant_ovals[(plant.x, plant.y)] = oval_id
    
    def render_creatures(self, creatures: List) -> None:
        """
        Render all creatures.
        
        Args:
            creatures: List of Creature objects
        """
        # Clear old creatures
        for oval_id in self.creature_ovals.values():
            self.canvas.delete(oval_id)
        self.creature_ovals.clear()
        
        # Draw current creatures
        for creature in creatures:
            if not creature.is_alive:
                continue
            
            size_multiplier = creature.get_size()
            margin = int(config.TILE_SIZE * (1 - size_multiplier) / 2)
            
            x1 = creature.x * config.TILE_SIZE + margin
            y1 = creature.y * config.TILE_SIZE + margin
            x2 = (creature.x + 1) * config.TILE_SIZE - margin
            y2 = (creature.y + 1) * config.TILE_SIZE - margin
            
            oval_id = self.canvas.create_oval(
                x1, y1, x2, y2,
                fill=creature.get_color(),
                outline='black',
                width=1
            )
            self.creature_ovals[id(creature)] = oval_id
    
    def clear(self) -> None:
        """Clear all rendered elements."""
        self.canvas.delete('all')
        self.tile_rectangles.clear()
        self.plant_ovals.clear()
        self.creature_ovals.clear()
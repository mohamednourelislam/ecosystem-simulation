"""
Renderer - handles all drawing to the Tkinter canvas.
Completely isolated from simulation logic.
"""

import tkinter as tk
from typing import List
from models.world import World
from models.tile import Tile
from models.plant import Plant
import config


class Renderer:
    """
    Responsible for rendering the simulation state to canvas.
    Pure view component with no business logic.
    """
    
    def __init__(self, canvas: tk.Canvas):
        """
        Initialize renderer with canvas.
        
        Args:
            canvas: Tkinter canvas to draw on
        """
        self.canvas = canvas
        self.tile_rectangles = {}  # Cache tile rectangle IDs
        self.plant_ovals = {}  # Cache plant oval IDs
        
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
        """
        Render the terrain grid.
        Called once at initialization, as terrain is static.
        
        Args:
            grid: 2D list of Tile objects
        """
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
        """
        Render all plants.
        Called each frame to update plant positions.
        
        Args:
            plants: List of Plant objects
        """
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
    
    def clear(self) -> None:
        """Clear all rendered elements."""
        self.canvas.delete('all')
        self.tile_rectangles.clear()
        self.plant_ovals.clear()
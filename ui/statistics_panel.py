"""
Statistics panel - displays real-time simulation stats.
Implements Observer pattern to react to world changes.
"""

import tkinter as tk
from observers.simulation_observer import SimulationObserver
from models.world import World
import config

class StatisticsPanel(tk.Frame, SimulationObserver):
    """
    Sidebar panel displaying simulation statistics.
    Observes world state and updates automatically.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize statistics panel.
        
        Args:
            parent: Parent Tkinter widget
        """
        super().__init__(parent, bg=config.COLORS['sidebar_bg'], width=config.SIDEBAR_WIDTH)
        self.pack_propagate(False)
        
        # Title
        title = tk.Label(
            self,
            text="Ecosystem Statistics",
            font=('Arial', 14, 'bold'),
            bg=config.COLORS['sidebar_bg']
        )
        title.pack(pady=20)
        
        # Statistics labels
        self.stats_labels = {}
        self._create_stat_labels()
        
    def _create_stat_labels(self) -> None:
        """Create label widgets for each statistic."""
        stats_config = [
            ('land_tiles', 'Land Tiles:'),
            ('water_tiles', 'Water Tiles:'),
            ('plant_count', 'Current Plants:'),
            ('max_plants', 'Max Plants:'),
            ('simulation_ticks', 'Simulation Ticks:'),
        ]
        
        for key, label_text in stats_config:
            frame = tk.Frame(self, bg=config.COLORS['sidebar_bg'])
            frame.pack(fill='x', padx=20, pady=5)
            
            label = tk.Label(
                frame,
                text=label_text,
                font=('Arial', 10),
                bg=config.COLORS['sidebar_bg'],
                anchor='w'
            )
            label.pack(side='left')
            
            value_label = tk.Label(
                frame,
                text='0',
                font=('Arial', 10, 'bold'),
                bg=config.COLORS['sidebar_bg'],
                anchor='e'
            )
            value_label.pack(side='right')
            
            self.stats_labels[key] = value_label
    
    def on_world_changed(self, world: World) -> None:
        """
        Observer callback - update display when world changes.
        
        Args:
            world: The world that changed
        """
        stats = world.get_statistics()
        
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))
"""
Main application - orchestrates all components.
Implements MVC controller pattern.
"""

import tkinter as tk
from models.world import World
from services.terrain_generator import TerrainGeneratorFactory
from services.plant_spawner import PlantSpawner
from strategies.spawn_probability import FertilityBasedStrategy
from ui.renderer import Renderer
from ui.statistics_panel import StatisticsPanel
import config


class SimulationApp:
    """
    Main application controller.
    Orchestrates simulation loop, coordinates components.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the simulation application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("2D Ecosystem Simulation - Fertility-Based")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Initialize model
        self.world = World()
        
        # Initialize services with dependency injection
        # Using fertility-based strategy for realistic vegetation patterns
        self.terrain_generator = TerrainGeneratorFactory(config.TERRAIN_SEED)
        spawn_strategy = FertilityBasedStrategy()
        self.plant_spawner = PlantSpawner(spawn_strategy)
        
        # Setup UI
        self._setup_ui()
        
        # Generate initial world state
        self._initialize_world()
        
        # Start simulation loop
        self.running = True
        self._schedule_update()
        self._schedule_plant_spawn()
    
    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        # Main container
        main_container = tk.Frame(self.root, bg=config.COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Canvas for simulation
        self.canvas = tk.Canvas(
            main_container,
            width=config.CANVAS_WIDTH,
            height=config.CANVAS_HEIGHT,
            bg=config.COLORS['background'],
            highlightthickness=0
        )
        self.canvas.pack(side='left')
        
        # Statistics panel (implements Observer)
        self.stats_panel = StatisticsPanel(main_container)
        self.stats_panel.pack(side='right', fill='y')
        
        # Attach observer to world
        self.world.attach_observer(self.stats_panel)
        
        # Initialize renderer
        self.renderer = Renderer(self.canvas)
    
    def _initialize_world(self) -> None:
        """Generate and render initial world state."""
        # Generate terrain using factory (now includes fertility calculation)
        terrain = self.terrain_generator.generate_terrain(
            config.GRID_WIDTH,
            config.GRID_HEIGHT
        )
        self.world.set_terrain(terrain)
    
        # Render static terrain (now shows fertility gradient)
        self.renderer.render_terrain(terrain)

    def _update(self) -> None:
        """
        Main simulation update tick.
        Updates world state and renders changes.
        """
        if not self.running:
            return

        # Update simulation state
        self.world.update()

        # Render dynamic elements
        self.renderer.render_plants(self.world.plants)

        # Schedule next update
        self._schedule_update()

    def _try_spawn_plant(self) -> None:
        """
        Attempt to spawn a plant.
        Runs on separate timer from main update.
        """
        if not self.running:
            return

        self.plant_spawner.attempt_spawn(self.world)

        # Schedule next spawn attempt
        self._schedule_plant_spawn()

    def _schedule_update(self) -> None:
        """Schedule next simulation update."""
        self.root.after(config.UPDATE_INTERVAL, self._update)

    def _schedule_plant_spawn(self) -> None:
        """Schedule next plant spawn attempt."""
        self.root.after(config.PLANT_SPAWN_INTERVAL, self._try_spawn_plant)

    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()
        
def main():
    """Application entry point."""
    root = tk.Tk()
    app = SimulationApp(root)
    app.run()
    
if __name__ == '__main__':
    main()
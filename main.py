"""
Main application - orchestrates all components.
"""

import tkinter as tk
import random
from models.world import World
from models.creature import Creature, Gender, LifeStage
from services.terrain_generator import TerrainGeneratorFactory
from services.plant_spawner import PlantSpawner
from services.creature_manager import CreatureManager
from strategies.spawn_probability import FertilityBasedStrategy
from ui.renderer import Renderer
from ui.control_panel import ControlPanel
import config


class SimulationApp:
    """Main application controller."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("2D Ecosystem Simulation - Interactive")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        
        # Simulation state
        self.running = False
        self.initialized = False
        self.update_job = None
        self.spawn_job = None
        self.creature_job = None
        self.tick_count = 0
        
        # Configuration
        self.current_config = None
        
        # Components
        self.world = None
        self.terrain_generator = None
        self.plant_spawner = None
        self.creature_manager = None
        self.renderer = None
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the user interface components."""
        main_container = tk.Frame(self.root, bg=config.COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(
            main_container,
            width=config.CANVAS_WIDTH,
            height=config.CANVAS_HEIGHT,
            bg=config.COLORS['background'],
            highlightthickness=0
        )
        self.canvas.pack(side='left')
        
        self.control_panel = ControlPanel(
            main_container,
            on_start=self._handle_start,
            on_pause=self._handle_pause,
            on_step=self._handle_step,
            on_restart=self._handle_restart
        )
        self.control_panel.pack(side='right', fill='y')
        
        self.renderer = Renderer(self.canvas)
        self.renderer.render_initial_blank()
    
    def _handle_start(self) -> None:
        """Handle start/resume action."""
        if not self.initialized:
            self._initialize_simulation()
            self.initialized = True
        
        self.running = True
        self._schedule_update()
        self._schedule_plant_spawn()
        self._schedule_creature_update()
    
    def _handle_pause(self) -> None:
        """Handle pause action."""
        self.running = False
        self._cancel_scheduled_jobs()
    
    def _handle_step(self) -> None:
        """Handle single step action."""
        if self.initialized and not self.running:
            self._update()
            self._try_spawn_plant()
            self._update_creatures()
    
    def _handle_restart(self) -> None:
        """Handle restart action."""
        self.running = False
        self.initialized = False
        self.tick_count = 0

        self._cancel_scheduled_jobs()

        if self.world:
            self.world.clear()

        self.renderer.clear()
        self.renderer.render_initial_blank()

        self.control_panel.update_statistics({
            'plant_count': 0,
            'creature_count': 0,
            'male_count': 0,
            'female_count': 0,
            'newborn_count': 0,
            'adult_count': 0,
            'land_tiles': 0,
            'water_tiles': 0,
            'avg_fertility': 0.0,
            'sim_time': 0
        })
        
    def _initialize_simulation(self) -> None:
        """Initialize simulation with current configuration."""
        self.current_config = self.control_panel.get_configuration()

        # Initialize world
        self.world = World(
            max_plants=self.current_config['max_plants'],
            max_creatures=self.current_config['max_creatures']
        )

        # Initialize services
        self.terrain_generator = TerrainGeneratorFactory(
            seed=int(self.current_config['terrain_seed'])
        )

        spawn_strategy = FertilityBasedStrategy(
            base_probability=self.current_config['base_spawn_probability'],
            fertility_multiplier=self.current_config['fertility_spawn_multiplier']
        )
        self.plant_spawner = PlantSpawner(spawn_strategy)

        self.creature_manager = CreatureManager()

        # Generate terrain
        terrain = self.terrain_generator.generate_terrain(
            config.GRID_WIDTH,
            config.GRID_HEIGHT,
            sea_level=self.current_config['sea_level'],
            fertility_max_distance=int(self.current_config['fertility_max_distance']),
            fertility_falloff_rate=self.current_config['fertility_falloff_rate']
        )
        self.world.set_terrain(terrain)

        # Spawn initial creatures
        self._spawn_initial_creatures()

        # Render
        self.renderer.render_terrain(terrain)
        self.renderer.render_creatures(self.world.creatures)

        self._update_statistics()
        
    def _spawn_initial_creatures(self) -> None:
        """Spawn initial creatures on land tiles."""
        num_creatures = self.current_config['initial_creatures']

        # Find suitable land tiles
        land_tiles = []
        for row in self.world.grid:
            for tile in row:
                if tile.can_support_plant():  # Land tiles
                    land_tiles.append((tile.x, tile.y))

        if not land_tiles:
            return

        # Spawn creatures
        for _ in range(num_creatures):
            x, y = random.choice(land_tiles)
            gender = random.choice([Gender.MALE, Gender.FEMALE])
            creature = Creature(x, y, gender, LifeStage.ADULT)
            creature.plants_eaten = 10  # Start with some food
            self.world.add_creature(creature)
            
    def _update(self) -> None:
        """Main simulation update tick."""
        if not self.running or not self.initialized:
            return

        self.world.update()
        self.tick_count += 1

        # Render
        self.renderer.render_plants(self.world.plants)
        self.renderer.render_creatures(self.world.creatures)

        # Update statistics periodically
        if self.tick_count % 10 == 0:
            self._update_statistics()

        self._schedule_update()
        
    def _try_spawn_plant(self) -> None:
        """Attempt to spawn a plant."""
        if not self.running or not self.initialized:
            return

        self.plant_spawner.attempt_spawn(self.world)
        self._schedule_plant_spawn()

    def _update_creatures(self) -> None:
        """Update creature behaviors."""
        if not self.running or not self.initialized:
            return

        self.creature_manager.update_creatures(self.world)
        self._schedule_creature_update()

    def _update_statistics(self) -> None:
        """Update statistics display."""
        if not self.world:
            return

        stats = self.world.get_statistics()
        stats['sim_time'] = self.tick_count * config.UPDATE_INTERVAL // 1000

        self.control_panel.update_statistics(stats)
        
    def _schedule_update(self) -> None:
        """Schedule next simulation update."""
        if self.running:
            self.update_job = self.root.after(config.UPDATE_INTERVAL, self._update)

    def _schedule_plant_spawn(self) -> None:
        """Schedule next plant spawn attempt."""
        if self.running and self.current_config:
            interval = int(self.current_config['plant_spawn_interval'])
            self.spawn_job = self.root.after(interval, self._try_spawn_plant)

    def _schedule_creature_update(self) -> None:
        """Schedule next creature update."""
        if self.running:
            self.creature_job = self.root.after(
                config.DEFAULT_CREATURE_UPDATE_INTERVAL,
                self._update_creatures
            )

    def _cancel_scheduled_jobs(self) -> None:
        """Cancel all scheduled jobs."""
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)
            self.spawn_job = None
        if self.creature_job:
            self.root.after_cancel(self.creature_job)
            self.creature_job = None
            
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
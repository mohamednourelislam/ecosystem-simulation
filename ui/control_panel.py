"""
Control panel for simulation configuration and controls.
Allows user to configure parameters before running and control execution.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any
import config


class ControlPanel(tk.Frame):
    """
    Interactive control panel for simulation configuration and execution control.
    Provides pre-launch configuration and runtime controls.
    """
    
    def __init__(self, parent, on_start: Callable, on_pause: Callable, 
                 on_step: Callable, on_restart: Callable):
        """
        Initialize control panel.
        
        Args:
            parent: Parent widget
            on_start: Callback for start/resume button
            on_pause: Callback for pause button
            on_step: Callback for single step button
            on_restart: Callback for restart button
        """
        super().__init__(parent, bg=config.COLORS['sidebar_bg'], width=config.SIDEBAR_WIDTH)
        
        self.on_start = on_start
        self.on_pause = on_pause
        self.on_step = on_step
        self.on_restart = on_restart
        
        self.is_running = False
        self.is_initialized = False
        
        # Store configuration values
        self.config_vars: Dict[str, tk.Variable] = {}
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup the control panel UI."""
        # Title
        title = tk.Label(
            self,
            text="Ecosystem Simulation",
            font=('Arial', 14, 'bold'),
            bg=config.COLORS['sidebar_bg']
        )
        title.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configuration tab
        self.config_frame = tk.Frame(self.notebook, bg=config.COLORS['sidebar_bg'])
        self.notebook.add(self.config_frame, text='Configuration')
        
        # Statistics tab
        self.stats_frame = tk.Frame(self.notebook, bg=config.COLORS['sidebar_bg'])
        self.notebook.add(self.stats_frame, text='Statistics')
        
        # Setup configuration controls
        self._setup_configuration_tab()
        
        # Setup statistics display
        self._setup_statistics_tab()
        
        # Control buttons at bottom
        self._setup_control_buttons()
    
    def _setup_configuration_tab(self) -> None:
        """Setup the configuration tab with adjustable parameters."""
        # Scrollable frame for many parameters
        canvas = tk.Canvas(self.config_frame, bg=config.COLORS['sidebar_bg'], 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.config_frame, orient="vertical", 
                                 command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=config.COLORS['sidebar_bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Terrain Section
        self._add_section_header(scrollable_frame, "Terrain Generation")
        self._add_config_slider(scrollable_frame, "Terrain Seed", 
                               "terrain_seed", 0, 100, 
                               config.DEFAULT_TERRAIN_SEED)
        self._add_config_slider(scrollable_frame, "Sea Level", 
                               "sea_level", 0.1, 0.6, 
                               config.DEFAULT_SEA_LEVEL, resolution=0.01)
        
        # Fertility Section
        self._add_section_header(scrollable_frame, "Fertility System")
        self._add_config_slider(scrollable_frame, "Max Distance", 
                               "fertility_max_distance", 5, 30, 
                               config.DEFAULT_FERTILITY_MAX_DISTANCE)
        self._add_config_slider(scrollable_frame, "Falloff Rate", 
                               "fertility_falloff_rate", 0.01, 0.2, 
                               config.DEFAULT_FERTILITY_FALLOFF_RATE, 
                               resolution=0.01)
        
        # Plant Section
        self._add_section_header(scrollable_frame, "Plant Settings")
        self._add_config_slider(scrollable_frame, "Max Plants", 
                               "max_plants", 50, 500, 
                               config.DEFAULT_MAX_PLANTS)
        self._add_config_slider(scrollable_frame, "Spawn Interval (ms)", 
                               "plant_spawn_interval", 50, 1000, 
                               config.DEFAULT_PLANT_SPAWN_INTERVAL, 
                               resolution=50)
        self._add_config_slider(scrollable_frame, "Base Spawn Probability", 
                               "base_spawn_probability", 0.01, 0.3, 
                               config.DEFAULT_BASE_SPAWN_PROBABILITY, 
                               resolution=0.01)
        self._add_config_slider(scrollable_frame, "Fertility Multiplier", 
                               "fertility_spawn_multiplier", 1.0, 5.0, 
                               config.DEFAULT_FERTILITY_SPAWN_MULTIPLIER, 
                               resolution=0.1)
        
        # Creature Section
        self._add_section_header(scrollable_frame, "Creature Settings")
        self._add_config_slider(scrollable_frame, "Max Creatures", 
                               "max_creatures", 10, 100, 
                               config.DEFAULT_MAX_CREATURES)
        self._add_config_slider(scrollable_frame, "Initial Creatures", 
                               "initial_creatures", 2, 30, 
                           config.DEFAULT_INITIAL_CREATURES)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _add_section_header(self, parent: tk.Frame, text: str) -> None:
        """Add a section header to organize parameters."""
        header = tk.Label(
            parent,
            text=text,
            font=('Arial', 10, 'bold'),
            bg=config.COLORS['sidebar_bg'],
            fg='#333333'
        )
        header.pack(anchor='w', padx=10, pady=(15, 5))
        
        separator = tk.Frame(parent, height=1, bg='#CCCCCC')
        separator.pack(fill='x', padx=10, pady=(0, 5))
    
    def _add_config_slider(self, parent: tk.Frame, label: str, 
                          var_name: str, from_: float, to: float, 
                          default: float, resolution: float = 1) -> None:
        """
        Add a configuration slider with label and value display.
        
        Args:
            parent: Parent frame
            label: Display label
            var_name: Variable name for storage
            from_: Minimum value
            to: Maximum value
            default: Default value
            resolution: Slider resolution
        """
        container = tk.Frame(parent, bg=config.COLORS['sidebar_bg'])
        container.pack(fill='x', padx=10, pady=5)
        
        # Determine if we need IntVar or DoubleVar
        if resolution >= 1:
            var = tk.IntVar(value=int(default))
        else:
            var = tk.DoubleVar(value=default)
        
        self.config_vars[var_name] = var
        
        # Label and value display
        label_frame = tk.Frame(container, bg=config.COLORS['sidebar_bg'])
        label_frame.pack(fill='x')
        
        lbl = tk.Label(
            label_frame,
            text=label + ":",
            font=('Arial', 9),
            bg=config.COLORS['sidebar_bg'],
            anchor='w'
        )
        lbl.pack(side='left')
        
        value_label = tk.Label(
            label_frame,
            textvariable=var,
            font=('Arial', 9, 'bold'),
            bg=config.COLORS['sidebar_bg'],
            fg='#0066CC',
            anchor='e'
        )
        value_label.pack(side='right')
        
        # Slider
        slider = tk.Scale(
            container,
            from_=from_,
            to=to,
            resolution=resolution,
            orient='horizontal',
            variable=var,
            showvalue=False,
            bg=config.COLORS['sidebar_bg'],
            highlightthickness=0,
            sliderrelief='flat'
        )
        slider.pack(fill='x')
    
    def _setup_statistics_tab(self) -> None:
        """Setup the statistics display tab."""
        self.stats_labels = {}
        
        stats = [
            ('Plants', 'plant_count'),
            ('Creatures', 'creature_count'),
            ('Males', 'male_count'),
            ('Females', 'female_count'),
            ('Newborns', 'newborn_count'),
            ('Adults', 'adult_count'),
            ('Land Tiles', 'land_tiles'),
            ('Water Tiles', 'water_tiles'),
            ('Avg Fertility', 'avg_fertility'),
            ('Simulation Time', 'sim_time')
        ]
        
        for display_name, key in stats:
            self._add_stat_display(self.stats_frame, display_name, key)
    
    def _add_stat_display(self, parent: tk.Frame, label: str, key: str) -> None:
        """Add a statistic display row."""
        container = tk.Frame(parent, bg=config.COLORS['sidebar_bg'])
        container.pack(fill='x', padx=10, pady=5)
        
        lbl = tk.Label(
            container,
            text=label + ":",
            font=('Arial', 10),
            bg=config.COLORS['sidebar_bg'],
            anchor='w'
        )
        lbl.pack(side='left')
        
        value_label = tk.Label(
            container,
            text="0",
            font=('Arial', 10, 'bold'),
            bg=config.COLORS['sidebar_bg'],
            fg='#0066CC',
            anchor='e'
        )
        value_label.pack(side='right')
        
        self.stats_labels[key] = value_label
    
    def _setup_control_buttons(self) -> None:
        """Setup control buttons (Start, Pause, Step, Restart)."""
        button_frame = tk.Frame(self, bg=config.COLORS['sidebar_bg'])
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        # Start/Resume button
        self.start_button = tk.Button(
            button_frame,
            text="▶ Start",
            command=self._handle_start,
            bg=config.COLORS['button_bg'],
            fg=config.COLORS['button_fg'],
            font=('Arial', 11, 'bold'),
            relief='raised',
            cursor='hand2'
        )
        self.start_button.pack(fill='x', pady=2)
        
        # Pause button
        self.pause_button = tk.Button(
            button_frame,
            text="⏸ Pause",
            command=self._handle_pause,
            bg=config.COLORS['button_pause'],
            fg=config.COLORS['button_fg'],
            font=('Arial', 11, 'bold'),
            relief='raised',
            cursor='hand2',
            state='disabled'
        )
        self.pause_button.pack(fill='x', pady=2)
        
        # Step button
        self.step_button = tk.Button(
            button_frame,
            text="⏭ Next Step",
            command=self._handle_step,
            bg='#2196F3',
            fg=config.COLORS['button_fg'],
            font=('Arial', 10),
            relief='raised',
            cursor='hand2',
            state='disabled'
        )
        self.step_button.pack(fill='x', pady=2)
        
        # Restart button
        self.restart_button = tk.Button(
            button_frame,
            text="🔄 Restart",
            command=self._handle_restart,
            bg=config.COLORS['button_stop'],
            fg=config.COLORS['button_fg'],
            font=('Arial', 10),
            relief='raised',
            cursor='hand2',
            state='disabled'
        )
        self.restart_button.pack(fill='x', pady=2)
    
    def _handle_start(self) -> None:
        """Handle start/resume button click."""
        if not self.is_initialized:
            # First launch - disable configuration
            self._lock_configuration()
            self.is_initialized = True
        
        self.is_running = True
        self.start_button.config(state='disabled')
        self.pause_button.config(state='normal')
        self.step_button.config(state='disabled')
        self.restart_button.config(state='normal')
        
        self.on_start()
    
    def _handle_pause(self) -> None:
        """Handle pause button click."""
        self.is_running = False
        self.start_button.config(state='normal', text="▶ Resume")
        self.pause_button.config(state='disabled')
        self.step_button.config(state='normal')
        
        self.on_pause()
    
    def _handle_step(self) -> None:
        """Handle step button click."""
        self.on_step()
    
    def _handle_restart(self) -> None:
        """Handle restart button click."""
        self.is_running = False
        self.is_initialized = False
        
        self._unlock_configuration()
        
        self.start_button.config(state='normal', text="▶ Start")
        self.pause_button.config(state='disabled')
        self.step_button.config(state='disabled')
        self.restart_button.config(state='disabled')
        
        self.on_restart()
    
    def _lock_configuration(self) -> None:
        """Disable configuration controls during simulation."""
        for widget in self.config_frame.winfo_children():
            self._set_widget_state(widget, 'disabled')
    
    def _unlock_configuration(self) -> None:
        """Enable configuration controls."""
        for widget in self.config_frame.winfo_children():
            self._set_widget_state(widget, 'normal')
    
    def _set_widget_state(self, widget, state: str) -> None:
        """Recursively set widget state."""
        try:
            widget.config(state=state)
        except tk.TclError:
            pass
        
        for child in widget.winfo_children():
            self._set_widget_state(child, state)
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current configuration values.
        
        Returns:
            Dictionary of configuration parameters
        """
        return {key: var.get() for key, var in self.config_vars.items()}
    
    def update_statistics(self, stats: Dict[str, Any]) -> None:
        """
        Update statistics display.
        
        Args:
            stats: Dictionary of statistics to display
        """
        for key, value in stats.items():
            if key in self.stats_labels:
                if isinstance(value, float):
                    self.stats_labels[key].config(text=f"{value:.2f}")
                else:
                    self.stats_labels[key].config(text=str(value))
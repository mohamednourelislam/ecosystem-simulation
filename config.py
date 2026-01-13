"""
Configuration constants for the ecosystem simulation.
Centralizes all magic numbers for easy adjustment.
"""

# Window and canvas dimensions
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 1000
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000
SIDEBAR_WIDTH = 300

# Grid configuration
TILE_SIZE = 10  # Size of each tile in pixels (100x100 grid)
GRID_WIDTH = CANVAS_WIDTH // TILE_SIZE
GRID_HEIGHT = CANVAS_HEIGHT // TILE_SIZE

# Terrain generation
TERRAIN_SEED = 42  # For reproducible terrain
WATER_THRESHOLD = 0.35  # Proportion of noise that becomes water (legacy)
SEA_LEVEL = 0.35  # Height threshold: below = water, above = land

# Fertility system
FERTILITY_MAX_DISTANCE = 15  # Max distance for fertility calculation
FERTILITY_FALLOFF_RATE = 0.08  # How quickly fertility decreases with distance
MIN_FERTILITY = 0.1  # Minimum fertility for far inland tiles
MAX_FERTILITY = 1.0  # Maximum fertility at water's edge

# Plant configuration
MAX_PLANTS = 200
PLANT_SPAWN_INTERVAL = 200  # milliseconds
BASE_SPAWN_PROBABILITY = 0.08  # Base chance per eligible tile (reduced since fertility boosts it)
FERTILITY_SPAWN_MULTIPLIER = 3.0  # How much fertility affects spawn rate

# Visual settings - Fertility gradient (light inland -> dark near water)
FERTILITY_COLORS = {
    'infertile': '#C4A57B',  # Light tan/beige (dry, poor soil)
    'low': '#A8956C',        # Light olive-brown
    'medium_low': '#8B9D5C',  # Yellow-green
    'medium': '#6B8E4D',     # Medium olive green
    'medium_high': '#4A7C3E', # Rich green
    'high': '#2D6B2F',       # Deep forest green
    'very_high': '#1A5520',  # Very dark rich green
}

COLORS = {
    'water': '#1E90FF',
    'land': '#8B7355',  # Legacy fallback
    'plant': '#0A3D0F',  # Very dark, rich forest green (darker than any land)
    'background': '#F0F0F0',
    'sidebar_bg': '#E0E0E0'
}

# Simulation timing
UPDATE_INTERVAL = 100  # milliseconds between updates
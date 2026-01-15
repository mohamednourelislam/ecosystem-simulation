"""
Configuration constants for the ecosystem simulation.
"""

# Window and canvas dimensions
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 1000
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 1000
SIDEBAR_WIDTH = 300

# Grid configuration
TILE_SIZE = 10
GRID_WIDTH = CANVAS_WIDTH // TILE_SIZE
GRID_HEIGHT = CANVAS_HEIGHT // TILE_SIZE

# Terrain generation
DEFAULT_TERRAIN_SEED = 42
DEFAULT_SEA_LEVEL = 0.35

# Fertility system
DEFAULT_FERTILITY_MAX_DISTANCE = 15
DEFAULT_FERTILITY_FALLOFF_RATE = 0.08
MIN_FERTILITY = 0.1
MAX_FERTILITY = 1.0

# Plant configuration
DEFAULT_MAX_PLANTS = 300
DEFAULT_PLANT_SPAWN_INTERVAL = 200
DEFAULT_BASE_SPAWN_PROBABILITY = 0.08
DEFAULT_FERTILITY_SPAWN_MULTIPLIER = 8.0  # Increased for better clustering

# Creature configuration - NEW
DEFAULT_MAX_CREATURES = 50
DEFAULT_INITIAL_CREATURES = 10
DEFAULT_CREATURE_UPDATE_INTERVAL = 100  # ms between creature updates

# Visual settings
FERTILITY_COLORS = {
    'infertile': '#C4A57B',
    'low': '#A8956C',
    'medium_low': '#8B9D5C',
    'medium': '#6B8E4D',
    'medium_high': '#4A7C3E',
    'high': '#2D6B2F',
    'very_high': '#1A5520',
}

COLORS = {
    'water': '#1E90FF',
    'land': '#8B7355',
    'plant': '#0A3D0F',
    'creature_male_adult': '#0000FF',
    'creature_female_adult': '#FF1493',
    'creature_male_newborn': '#87CEEB',
    'creature_female_newborn': '#FFB6C1',
    'background': '#F0F0F0',
    'sidebar_bg': '#E0E0E0',
    'button_bg': '#4CAF50',
    'button_fg': '#FFFFFF',
    'button_pause': '#FF9800',
    'button_stop': '#F44336'
}

# Simulation timing
UPDATE_INTERVAL = 100
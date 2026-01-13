"""
Factory pattern implementation for terrain generation.
Encapsulates complex procedural generation logic using heightmap with hydraulic erosion.
Now includes fertility calculation based on water proximity.
"""

import random
import math
from typing import List, Tuple
from models.tile import Tile, LandTile, WaterTile
import config


class TerrainGeneratorFactory:
    """
    Factory for creating terrain grids with procedural generation.
    Uses heightmap-based generation with hydraulic erosion for realistic terrain.
    Calculates fertility for each land tile based on water proximity.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize generator with optional seed.
        
        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed or config.TERRAIN_SEED
        self.random = random.Random(self.seed)
    
    def generate_terrain(self, width: int, height: int) -> List[List[Tile]]:
        """
        Generate a terrain grid using heightmap with hydraulic erosion.
        
        Pipeline:
        1. Generate base heightmap using Perlin-like noise
        2. Apply hydraulic erosion for realistic features
        3. Classify heights into water/land using sea level
        4. Calculate fertility for all land tiles
        5. Create tile objects with fertility values
        
        Args:
            width: Grid width in tiles
            height: Grid height in tiles
            
        Returns:
            2D list of Tile objects (with fertility for land tiles)
        """
        # Step 1: Generate base heightmap
        heightmap = self._generate_heightmap(width, height)
        
        # Step 2: Apply hydraulic erosion
        heightmap = self._apply_hydraulic_erosion(heightmap, width, height)
        
        # Step 3: Create initial tile grid (needed for water identification)
        grid = self._heightmap_to_tiles_simple(heightmap, width, height)
        
        # Step 4: Calculate fertility map for all land tiles
        fertility_map = self._calculate_fertility_map(grid, width, height)
        
        # Step 5: Recreate tiles with fertility values
        grid = self._create_tiles_with_fertility(heightmap, fertility_map, width, height)
        
        return grid
    
    def _generate_heightmap(self, width: int, height: int) -> List[List[float]]:
        """
        Generate a 2D heightmap using simplified Perlin-like algorithm.
        Uses multiple octaves for varied terrain features.
        
        Args:
            width: Heightmap width
            height: Heightmap height
            
        Returns:
            2D list of float values in range [0, 1]
        """
        heightmap = [[0.0 for _ in range(width)] for _ in range(height)]
        
        # Multiple octaves for natural-looking terrain
        octaves = [
            (8, 1.0),    # Large features (mountains, plains)
            (16, 0.5),   # Medium features (hills)
            (32, 0.25),  # Fine details (small variations)
            (64, 0.125), # Very fine details
        ]
        
        for scale, amplitude in octaves:
            for y in range(height):
                for x in range(width):
                    sample_x = x / scale
                    sample_y = y / scale
                    noise_value = self._smooth_noise(sample_x, sample_y)
                    heightmap[y][x] += noise_value * amplitude
        
        # Normalize to [0, 1] range
        max_possible = sum(amp for _, amp in octaves)
        for y in range(height):
            for x in range(width):
                heightmap[y][x] = (heightmap[y][x] + max_possible) / (2 * max_possible)
        
        return heightmap
    
    def _apply_hydraulic_erosion(
        self, 
        heightmap: List[List[float]], 
        width: int, 
        height: int
    ) -> List[List[float]]:
        """
        Apply hydraulic erosion simulation to create realistic terrain features.
        
        Args:
            heightmap: Input heightmap to erode
            width: Map width
            height: Map height
            
        Returns:
            Eroded heightmap with values in [0, 1]
        """
        num_iterations = width * height // 2
        erosion_strength = 0.002
        deposition_strength = 0.001
        min_slope = 0.0001
        
        for _ in range(num_iterations):
            x = self.random.randint(0, width - 1)
            y = self.random.randint(0, height - 1)
            
            self._erode_path(
                heightmap, 
                x, y, 
                width, height,
                erosion_strength,
                deposition_strength,
                min_slope
            )
        
        self._clamp_heightmap(heightmap, width, height)
        
        return heightmap
    
    def _erode_path(
        self,
        heightmap: List[List[float]],
        start_x: int,
        start_y: int,
        width: int,
        height: int,
        erosion_strength: float,
        deposition_strength: float,
        min_slope: float
    ) -> None:
        """Simulate a single water droplet's erosion path."""
        x, y = start_x, start_y
        sediment = 0.0
        max_path_length = 100
        
        for _ in range(max_path_length):
            current_height = heightmap[y][x]
            
            next_x, next_y, next_height = self._find_lowest_neighbor(
                heightmap, x, y, width, height
            )
            
            height_diff = current_height - next_height
            
            if height_diff <= min_slope:
                if sediment > 0:
                    heightmap[y][x] += sediment * deposition_strength
                break
            
            erosion_amount = min(height_diff, erosion_strength)
            heightmap[y][x] -= erosion_amount
            sediment += erosion_amount
            
            if height_diff < erosion_strength:
                deposit_amount = sediment * deposition_strength
                heightmap[y][x] += deposit_amount
                sediment -= deposit_amount
            
            x, y = next_x, next_y
            
            if heightmap[y][x] < getattr(config, 'SEA_LEVEL', 0.35):
                break
    
    def _find_lowest_neighbor(
        self,
        heightmap: List[List[float]],
        x: int,
        y: int,
        width: int,
        height: int
    ) -> Tuple[int, int, float]:
        """Find the lowest neighboring cell (8-directional)."""
        current_height = heightmap[y][x]
        lowest_x, lowest_y = x, y
        lowest_height = current_height
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = x + dx, y + dy
                
                if 0 <= nx < width and 0 <= ny < height:
                    neighbor_height = heightmap[ny][nx]
                    
                    if neighbor_height < lowest_height:
                        lowest_x, lowest_y = nx, ny
                        lowest_height = neighbor_height
        
        return lowest_x, lowest_y, lowest_height
    
    def _clamp_heightmap(
        self, 
        heightmap: List[List[float]], 
        width: int, 
        height: int
    ) -> None:
        """Clamp all heightmap values to [0, 1] range."""
        for y in range(height):
            for x in range(width):
                heightmap[y][x] = max(0.0, min(1.0, heightmap[y][x]))
    
    def _heightmap_to_tiles_simple(
        self,
        heightmap: List[List[float]],
        width: int,
        height: int
    ) -> List[List[Tile]]:
        """
        Convert heightmap to simple tile grid (no fertility yet).
        Used for initial water identification.
        
        Args:
            heightmap: 2D heightmap with values in [0, 1]
            width: Grid width
            height: Grid height
            
        Returns:
            2D list of Tile objects (land tiles have default fertility)
        """
        sea_level = getattr(config, 'SEA_LEVEL', config.WATER_THRESHOLD)
        
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if heightmap[y][x] < sea_level:
                    tile = WaterTile(x, y)
                else:
                    tile = LandTile(x, y, fertility=0.5)  # Temporary fertility
                row.append(tile)
            grid.append(row)
        
        return grid
    
    def _calculate_fertility_map(
        self,
        grid: List[List[Tile]],
        width: int,
        height: int
    ) -> List[List[float]]:
        """
        Calculate fertility for each tile based on distance to nearest water.
        Creates smooth gradient from high fertility at water's edge to low inland.
        
        Args:
            grid: Tile grid (used to identify water locations)
            width: Map width
            height: Map height
            
        Returns:
            2D list of fertility values [0, 1]
        """
        fertility_map = [[0.0 for _ in range(width)] for _ in range(height)]
        
        # Find all water tiles for distance calculation
        water_positions = []
        for y in range(height):
            for x in range(width):
                if isinstance(grid[y][x], WaterTile):
                    water_positions.append((x, y))
        
        # Calculate fertility for each tile
        for y in range(height):
            for x in range(width):
                if isinstance(grid[y][x], LandTile):
                    # Find distance to nearest water
                    min_distance = self._find_nearest_water_distance_optimized(
                        x, y, water_positions, width, height
                    )
                    
                    # Convert distance to fertility using exponential falloff
                    fertility = self._distance_to_fertility(min_distance)
                    fertility_map[y][x] = fertility
        
        # Apply smoothing for more gradual transitions
        fertility_map = self._smooth_fertility_map(fertility_map, width, height)
        
        return fertility_map
    
    def _find_nearest_water_distance_optimized(
        self,
        x: int,
        y: int,
        water_positions: List[Tuple[int, int]],
        width: int,
        height: int
    ) -> float:
        """
        Find Euclidean distance to nearest water tile.
        Optimized to check only nearby water sources.
        
        Args:
            x: Tile x coordinate
            y: Tile y coordinate
            water_positions: List of all water tile coordinates
            width: Map width
            height: Map height
            
        Returns:
            Distance to nearest water
        """
        min_distance = float('inf')
        search_limit = config.FERTILITY_MAX_DISTANCE + 5
        
        for wx, wy in water_positions:
            # Quick Manhattan distance check for early pruning
            manhattan = abs(x - wx) + abs(y - wy)
            if manhattan > search_limit:
                continue
            
            # Calculate Euclidean distance
            distance = math.sqrt((x - wx) ** 2 + (y - wy) ** 2)
            min_distance = min(min_distance, distance)
            
            # Early exit if adjacent to water
            if min_distance <= 1.0:
                return min_distance
        
        return min_distance
    
    def _distance_to_fertility(self, distance: float) -> float:
        """
        Convert distance from water to fertility value.
        Uses exponential falloff for natural-looking gradient.
        
        Args:
            distance: Distance from nearest water
            
        Returns:
            Fertility value [MIN_FERTILITY, MAX_FERTILITY]
        """
        if distance == 0:
            return config.MAX_FERTILITY
        
        # Exponential falloff
        fertility = config.MAX_FERTILITY * math.exp(-config.FERTILITY_FALLOFF_RATE * distance)
        
        # Clamp to minimum
        return max(config.MIN_FERTILITY, min(config.MAX_FERTILITY, fertility))
    
    def _smooth_fertility_map(
        self,
        fertility_map: List[List[float]],
        width: int,
        height: int,
        iterations: int = 2
    ) -> List[List[float]]:
        """
        Apply smoothing to fertility map for gradual transitions.
        Uses box blur for computational efficiency.
        
        Args:
            fertility_map: Input fertility map
            width: Map width
            height: Map height
            iterations: Number of smoothing passes
            
        Returns:
            Smoothed fertility map
        """
        for _ in range(iterations):
            smoothed = [[0.0 for _ in range(width)] for _ in range(height)]
            
            for y in range(height):
                for x in range(width):
                    # Average with neighbors
                    total = 0.0
                    count = 0
                    
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                total += fertility_map[ny][nx]
                                count += 1
                    
                    smoothed[y][x] = total / count if count > 0 else fertility_map[y][x]
            
            fertility_map = smoothed
        
        return fertility_map
    
    def _create_tiles_with_fertility(
        self,
        heightmap: List[List[float]],
        fertility_map: List[List[float]],
        width: int,
        height: int
    ) -> List[List[Tile]]:
        """
        Create final tile grid with fertility values applied.
        
        Args:
            heightmap: Height values for water/land classification
            fertility_map: Fertility values for land tiles
            width: Grid width
            height: Grid height
            
        Returns:
            2D list of Tile objects with fertility
        """
        sea_level = getattr(config, 'SEA_LEVEL', config.WATER_THRESHOLD)
        
        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                if heightmap[y][x] < sea_level:
                    tile = WaterTile(x, y)
                else:
                    tile = LandTile(x, y, fertility=fertility_map[y][x])
                row.append(tile)
            grid.append(row)
        
        return grid
    
    def _smooth_noise(self, x: float, y: float) -> float:
        """Generate smooth noise value at continuous coordinates."""
        x_int = int(x)
        y_int = int(y)
        
        x_frac = x - x_int
        y_frac = y - y_int
        
        v1 = self._random_value(x_int, y_int)
        v2 = self._random_value(x_int + 1, y_int)
        v3 = self._random_value(x_int, y_int + 1)
        v4 = self._random_value(x_int + 1, y_int + 1)
        
        i1 = self._interpolate(v1, v2, x_frac)
        i2 = self._interpolate(v3, v4, x_frac)
        
        return self._interpolate(i1, i2, y_frac)
    
    def _random_value(self, x: int, y: int) -> float:
        """Get deterministic pseudo-random value for integer coordinates."""
        n = (x + self.seed) + (y + self.seed) * 57
        n = (n << 13) ^ n
        n = (n * (n * n * 15731 + 789221) + 1376312589) & 0x7fffffff
        return 1.0 - (n / 1073741824.0)
    
    def _interpolate(self, a: float, b: float, t: float) -> float:
        """Smooth interpolation between two values using cosine interpolation."""
        ft = t * math.pi
        f = (1 - math.cos(ft)) / 2
        return a * (1 - f) + b * f
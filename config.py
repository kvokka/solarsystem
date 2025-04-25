# config.py
import math

# --- Simulation Settings ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
UPDATE_DELAY_MS = 16  # Target ~60 FPS (1000ms / 60fps)
DEFAULT_SPEED_MODIFIER = 1.0
SPEED_MODIFIERS = [1.0, 0.1, 0.01] # Normal, Slow, Very Slow
INITIAL_SCALE = 1.0 # Initial zoom level
MIN_SCALE = 0.1
MAX_SCALE = 5.0
SCALE_STEP = 1.2 # Multiplier for zoom in/out
PAN_SPEED = 10 # Pixels per arrow key press

# --- Colors ---
BG_COLOR = "black"
SUN_COLOR = "yellow"
PLANET_COLORS = ["#8B4513", "#FFA500", "#ADD8E6", "#FF6347"] # Example colors
SATELLITE_COLOR = "gray"
ORBIT_COLOR = "dimgray"
LABEL_COLOR = "white"
MST_EDGE_COLOR = "cyan"
DATA_PACKET_COLOR = "lime green"

# --- Physics & Scale ---
# Using arbitrary units for distance and time. Adjust for desired visual scale.
AU = 150  # Astronomical Unit equivalent in pixels for visual scaling
SUN_RADIUS = 20
PLANET_BASE_RADIUS = 5
SATELLITE_RADIUS = 3
DATA_PACKET_RADIUS = 2
PLANET_ORBITS = [1 * AU, 1.8 * AU, 2.5 * AU, 3.5 * AU] # Example orbit radii
PLANET_ANGULAR_VELOCITIES = [0.01, 0.006, 0.004, 0.002] # Radians per update step (adjusted by speed)
SATELLITE_ORBIT_RADIUS_FACTOR = 0.2 # Satellite orbit radius relative to planet orbit
SATELLITE_ANGULAR_VELOCITY_FACTOR = 2.0 # Satellite speed relative to planet
DATA_PACKET_SPEED = 5.0 # Pixels per update step (adjusted by speed)

# --- Network Settings ---
NUM_SATELLITES_PER_PLANET = 2
MST_RECALCULATION_INTERVAL_S = 5 # Recalculate MST every 5 seconds
DATA_GENERATION_PROBABILITY = 0.01 # Probability per satellite per update step to generate a packet

# --- Logging ---
LOG_FILE = "log.txt"
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# --- Drawing ---
ORBIT_LINE_WIDTH = 1
MST_LINE_WIDTH = 1
LABEL_FONT = ("Arial", 8)

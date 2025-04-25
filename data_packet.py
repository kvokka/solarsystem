# data_packet.py
import math
import config
from utils import transform_coords, distance

class DataPacket:
    _id_counter = 0
    def __init__(self, origin, destination):
        DataPacket._id_counter += 1
        self.id = DataPacket._id_counter
        self.origin = origin        # Origin Satellite object
        self.destination = destination # Destination Satellite object
        self.current_sim_x, self.current_sim_y = origin.get_sim_pos()
        self.path = []              # List of Satellite objects representing the path
        self.path_index = 0         # Index of the next target satellite in the path
        self.target_sim_x = None    # Sim coords of the next satellite in the path
        self.target_sim_y = None
        self.reached_destination = False

        self.canvas_id = None # ID for the packet's oval on the canvas

    def set_path(self, path_satellites):
        """Sets the path (list of Satellite objects) and initializes the first target."""
        self.path = path_satellites
        self.path_index = 0
        if self.path:
            self._update_target()
        else:
            # No path found? Mark as finished immediately.
            self.reached_destination = True

    def _update_target(self):
        """Sets the next target satellite's position."""
        if self.path_index < len(self.path):
            next_satellite = self.path[self.path_index]
            self.target_sim_x, self.target_sim_y = next_satellite.get_sim_pos()
        else:
            # Should have reached destination if path was valid
            self.reached_destination = True
            self.target_sim_x = None
            self.target_sim_y = None


    def update_position(self, dt, speed_modifier):
        """Moves the packet towards the current target satellite."""
        if self.reached_destination or self.target_sim_x is None:
            return

        # Update target position in case the satellite moved
        if self.path_index < len(self.path):
            target_satellite = self.path[self.path_index]
            self.target_sim_x, self.target_sim_y = target_satellite.get_sim_pos()
        else:
             # Reached the end of the path
            self.reached_destination = True
            return

        # Move towards target
        dx = self.target_sim_x - self.current_sim_x
        dy = self.target_sim_y - self.current_sim_y
        dist_to_target = math.sqrt(dx**2 + dy**2)
        travel_dist = config.DATA_PACKET_SPEED * speed_modifier * dt

        if dist_to_target <= travel_dist:
            # Reached the current target satellite
            self.current_sim_x, self.current_sim_y = self.target_sim_x, self.target_sim_y
            self.path_index += 1
            if self.path_index >= len(self.path):
                # Reached the final destination
                self.reached_destination = True
                print(f"Packet {self.id} from {self.origin.name} reached {self.destination.name}") # Debug
                from logger_setup import logger # Local import
                logger.info(f"Packet {self.id} arrived: {self.origin.name} -> {self.destination.name}")
            else:
                # Set next target
                self._update_target()
        else:
            # Move along the vector towards the target
            move_ratio = travel_dist / dist_to_target
            self.current_sim_x += dx * move_ratio
            self.current_sim_y += dy * move_ratio

    def draw(self, canvas, scale, offset_x, offset_y):
        """Draws the data packet on the canvas."""
        if self.reached_destination:
            # Optionally delete graphic when reached
            self.delete_graphics(canvas)
            return

        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        cx, cy = transform_coords(self.current_sim_x, self.current_sim_y, canvas_width, canvas_height, scale, offset_x, offset_y)
        canvas_radius = max(1, config.DATA_PACKET_RADIUS * scale)

        if self.canvas_id:
            canvas.coords(self.canvas_id, cx - canvas_radius, cy - canvas_radius, cx + canvas_radius, cy + canvas_radius)
            canvas.itemconfig(self.canvas_id, fill=config.DATA_PACKET_COLOR, outline=config.DATA_PACKET_COLOR)
        else:
            self.canvas_id = canvas.create_oval(cx - canvas_radius, cy - canvas_radius, cx + canvas_radius, cy + canvas_radius, fill=config.DATA_PACKET_COLOR, outline=config.DATA_PACKET_COLOR, tags="data_packet")

    def delete_graphics(self, canvas):
        """Removes the packet's graphic from the canvas."""
        if self.canvas_id:
            canvas.delete(self.canvas_id)
        self.canvas_id = None

    # Reset counter if needed
    @classmethod
    def reset_counter(cls):
        cls._id_counter = 0

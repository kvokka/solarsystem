# celestial_body.py
import math
import random
import config
from utils import transform_coords

class CelestialBody:
    """Base class for all celestial bodies."""
    def __init__(self, name, sim_radius, color, sim_x=0, sim_y=0, orbit_radius=0, orbit_center_obj=None, angular_velocity=0):
        self.name = name
        self.sim_radius = sim_radius  # Radius in simulation units
        self.color = color
        self.sim_x = sim_x            # Position in simulation units
        self.sim_y = sim_y
        self.orbit_radius = orbit_radius # Orbit radius in simulation units
        self.orbit_center_obj = orbit_center_obj # Object it orbits (or None for Sun)
        self.angular_velocity = angular_velocity # Radians per update step
        self.current_angle = random.uniform(0, 2 * math.pi) # Initial orbital angle

        self.canvas_id = None # ID for the main oval on the canvas
        self.orbit_id = None  # ID for the orbit line on the canvas
        self.label_id = None  # ID for the label text on the canvas

    def get_sim_pos(self):
        return (self.sim_x, self.sim_y)

    def get_orbit_center_pos(self):
        if self.orbit_center_obj:
            return self.orbit_center_obj.get_sim_pos()
        return (0, 0) # Sun is at origin

    def update_position(self, dt, speed_modifier):
        """Updates position based on orbital mechanics."""
        if self.orbit_radius > 0 and self.orbit_center_obj is not None:
            center_x, center_y = self.get_orbit_center_pos()
            # Adjust angular velocity by delta time and speed modifier
            self.current_angle += self.angular_velocity * speed_modifier * dt
            self.current_angle %= (2 * math.pi) # Keep angle within 0 to 2pi

            self.sim_x = center_x + self.orbit_radius * math.cos(self.current_angle)
            self.sim_y = center_y + self.orbit_radius * math.sin(self.current_angle)
        elif self.orbit_center_obj is None: # Sun doesn't move
            pass

    def draw(self, canvas, scale, offset_x, offset_y, show_label, show_orbit):
        """Draws the celestial body, its orbit, and label on the canvas."""
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # Calculate canvas coordinates and scaled radius
        cx, cy = transform_coords(self.sim_x, self.sim_y, canvas_width, canvas_height, scale, offset_x, offset_y)
        canvas_radius = max(1, self.sim_radius * scale) # Ensure radius is at least 1 pixel

        # --- Draw Body ---
        if self.canvas_id:
            canvas.coords(self.canvas_id, cx - canvas_radius, cy - canvas_radius, cx + canvas_radius, cy + canvas_radius)
            canvas.itemconfig(self.canvas_id, fill=self.color, outline=self.color)
        else:
            self.canvas_id = canvas.create_oval(cx - canvas_radius, cy - canvas_radius, cx + canvas_radius, cy + canvas_radius, fill=self.color, outline=self.color, tags=("celestial_body", self.name))

        # --- Draw Orbit ---
        if show_orbit and self.orbit_radius > 0:
            center_x_sim, center_y_sim = self.get_orbit_center_pos()
            orbit_cx, orbit_cy = transform_coords(center_x_sim, center_y_sim, canvas_width, canvas_height, scale, offset_x, offset_y)
            orbit_r_canvas = self.orbit_radius * scale

            if self.orbit_id:
                canvas.coords(self.orbit_id, orbit_cx - orbit_r_canvas, orbit_cy - orbit_r_canvas, orbit_cx + orbit_r_canvas, orbit_cy + orbit_r_canvas)
                canvas.itemconfig(self.orbit_id, outline=config.ORBIT_COLOR, width=config.ORBIT_LINE_WIDTH, state='normal')
            else:
                 self.orbit_id = canvas.create_oval(orbit_cx - orbit_r_canvas, orbit_cy - orbit_r_canvas, orbit_cx + orbit_r_canvas, orbit_cy + orbit_r_canvas, outline=config.ORBIT_COLOR, width=config.ORBIT_LINE_WIDTH, tags=("orbit", self.name))
        elif self.orbit_id:
            canvas.itemconfig(self.orbit_id, state='hidden') # Hide if show_orbit is false

        # --- Draw Label ---
        if show_label:
            label_x = cx
            label_y = cy - canvas_radius - 5 # Position label above the body
            if self.label_id:
                canvas.coords(self.label_id, label_x, label_y)
                canvas.itemconfig(self.label_id, text=self.name, fill=config.LABEL_COLOR, font=config.LABEL_FONT, state='normal')
            else:
                self.label_id = canvas.create_text(label_x, label_y, text=self.name, fill=config.LABEL_COLOR, font=config.LABEL_FONT, tags=("label", self.name))
        elif self.label_id:
             canvas.itemconfig(self.label_id, state='hidden') # Hide if show_label is false

    def delete_graphics(self, canvas):
        """Removes graphics elements from the canvas."""
        if self.canvas_id: canvas.delete(self.canvas_id)
        if self.orbit_id: canvas.delete(self.orbit_id)
        if self.label_id: canvas.delete(self.label_id)
        self.canvas_id = self.orbit_id = self.label_id = None


class Sun(CelestialBody):
    def __init__(self):
        super().__init__(
            name="Sun",
            sim_radius=config.SUN_RADIUS,
            color=config.SUN_COLOR,
            sim_x=0,
            sim_y=0,
            orbit_radius=0,
            orbit_center_obj=None,
            angular_velocity=0
        )


class Planet(CelestialBody):
    def __init__(self, name, color, orbit_radius, angular_velocity, sun):
        super().__init__(
            name=name,
            sim_radius=config.PLANET_BASE_RADIUS + random.uniform(-1, 1), # Add some size variation
            color=color,
            orbit_radius=orbit_radius,
            orbit_center_obj=sun,
            angular_velocity=angular_velocity
        )
        # Initial position calculation
        self.update_position(0, 1.0) # Initial update with dt=0


class Satellite(CelestialBody):
    _id_counter = 0
    def __init__(self, planet):
        Satellite._id_counter += 1
        name = f"{planet.name}_Sat_{Satellite._id_counter}"
        orbit_radius = planet.orbit_radius * config.SATELLITE_ORBIT_RADIUS_FACTOR
        angular_velocity = planet.angular_velocity * config.SATELLITE_ANGULAR_VELOCITY_FACTOR * (1 if random.random() > 0.5 else -1) # Random direction

        super().__init__(
            name=name,
            sim_radius=config.SATELLITE_RADIUS,
            color=config.SATELLITE_COLOR,
            orbit_radius=orbit_radius,
            orbit_center_obj=planet,
            angular_velocity=angular_velocity
        )
        # Initial position calculation
        self.update_position(0, 1.0) # Initial update with dt=0

    def generate_data_packet(self, all_satellites, mst_edges):
        """
        Generates a data packet if probability allows.
        Selects a random destination satellite reachable via the current MST.
        Returns the new DataPacket object or None.
        """
        if random.random() < config.DATA_GENERATION_PROBABILITY:
            from data_packet import DataPacket # Avoid circular import

            # Find reachable satellites using the current MST
            reachable_satellites = set([self])
            queue = [self]
            visited = {self}
            while queue:
                current = queue.pop(0)
                # Check MST edges connected to the current satellite
                for u, v in mst_edges:
                    neighbor = None
                    if u == current and v not in visited:
                        neighbor = v
                    elif v == current and u not in visited:
                        neighbor = u

                    if neighbor:
                        visited.add(neighbor)
                        reachable_satellites.add(neighbor)
                        queue.append(neighbor)

            # Exclude self from possible destinations
            possible_destinations = list(reachable_satellites - {self})

            if possible_destinations:
                destination_satellite = random.choice(possible_destinations)
                # Pathfinding on MST will be handled by the Simulation class
                return DataPacket(origin=self, destination=destination_satellite)
        return None

    # Reset counter if needed, e.g., for multiple simulation instances
    @classmethod
    def reset_counter(cls):
        cls._id_counter = 0

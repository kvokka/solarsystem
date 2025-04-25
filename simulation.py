# simulation.py
import tkinter as tk
import time
import math
import random
import heapq # For potential future pathfinding like Dijkstra

import config
from logger_setup import logger
from utils import distance, line_segment_circle_collision, UnionFind, transform_coords
from celestial_body import Sun, Planet, Satellite
from data_packet import DataPacket

class Simulation:
    def __init__(self, canvas):
        self.canvas = canvas
        self.paused = False
        self.speed_modifier_index = 0 # Index in config.SPEED_MODIFIERS
        self.speed_modifier = config.SPEED_MODIFIERS[self.speed_modifier_index]
        self.scale = config.INITIAL_SCALE
        self.offset_x = 0
        self.offset_y = 0
        self.show_labels = True
        self.show_orbits = True

        self.celestial_bodies = []
        self.satellites = []
        self.planets = []
        self.sun = None
        self.obstacles = [] # Sun and Planets for collision checks

        self.data_packets = []
        self.mst_edges = [] # List of tuples: (satellite1, satellite2)
        self.mst_lines = [] # List of canvas line IDs for MST edges

        self.last_update_time = time.time()
        self.last_mst_recalculation_time = 0

        self._mouse_drag_start = None

        self._initialize_objects()
        self._bind_controls()
        logger.info("Simulation Started. Speed: 1x")

    def _initialize_objects(self):
        """Creates the sun, planets, and satellites."""
        # Reset counters if re-initializing
        Satellite.reset_counter()
        DataPacket.reset_counter()

        # Create Sun
        self.sun = Sun()
        self.celestial_bodies.append(self.sun)
        self.obstacles.append(self.sun) # Sun is an obstacle

        # Create Planets
        for i in range(len(config.PLANET_ORBITS)):
            planet = Planet(
                name=f"Planet_{i+1}",
                color=config.PLANET_COLORS[i % len(config.PLANET_COLORS)],
                orbit_radius=config.PLANET_ORBITS[i],
                angular_velocity=config.PLANET_ANGULAR_VELOCITIES[i],
                sun=self.sun
            )
            self.celestial_bodies.append(planet)
            self.planets.append(planet)
            self.obstacles.append(planet) # Planets are obstacles

            # Create Satellites for each Planet
            for _ in range(config.NUM_SATELLITES_PER_PLANET):
                satellite = Satellite(planet=planet)
                self.celestial_bodies.append(satellite)
                self.satellites.append(satellite)

        logger.info(f"Initialized {len(self.planets)} planets and {len(self.satellites)} satellites.")

    def _bind_controls(self):
        """Binds keyboard and mouse controls."""
        self.canvas.focus_set() # Make canvas receptive to key presses
        self.canvas.bind("<KeyPress>", self.handle_keypress)
        # Mouse panning
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan_motion)
        self.canvas.bind("<ButtonRelease-1>", self.end_pan)
        # Mouse zooming (platform-dependent)
        self.canvas.bind("<MouseWheel>", self.zoom_wheel) # Windows/MacOS
        self.canvas.bind("<Button-4>", lambda e: self.zoom(config.SCALE_STEP)) # Linux scroll up
        self.canvas.bind("<Button-5>", lambda e: self.zoom(1 / config.SCALE_STEP)) # Linux scroll down

    def handle_keypress(self, event):
        """Handles keyboard input."""
        key = event.keysym.lower()
        #print(f"Key pressed: {key}") # Debug

        if key == 'p':
            self.toggle_pause()
        elif key == 's':
            self.change_speed()
        elif key == 'l':
            self.toggle_labels()
        elif key == 'o':
            self.toggle_orbits()
        elif key == 'plus' or key == 'equal': # Numpad Plus or regular '+' (often needs shift)
            self.zoom(config.SCALE_STEP)
        elif key == 'minus' or key == 'underscore': # Numpad Minus or regular '-'
            self.zoom(1 / config.SCALE_STEP)
        elif key == 'left':
             self.offset_x += config.PAN_SPEED
        elif key == 'right':
             self.offset_x -= config.PAN_SPEED
        elif key == 'up':
             self.offset_y += config.PAN_SPEED
        elif key == 'down':
             self.offset_y -= config.PAN_SPEED
        elif key == 'r': # Reset view
            self.reset_view()

    def start_pan(self, event):
        self._mouse_drag_start = (event.x, event.y)

    def pan_motion(self, event):
        if self._mouse_drag_start:
            dx = event.x - self._mouse_drag_start[0]
            dy = event.y - self._mouse_drag_start[1]
            self.offset_x += dx
            self.offset_y += dy
            self._mouse_drag_start = (event.x, event.y) # Update start for next motion delta

    def end_pan(self, event):
        self._mouse_drag_start = None

    def zoom_wheel(self, event):
        # Determine zoom factor based on scroll direction
        if event.delta > 0: # Scroll up (Windows/MacOS)
            self.zoom(config.SCALE_STEP)
        elif event.delta < 0: # Scroll down
            self.zoom(1 / config.SCALE_STEP)

    def zoom(self, factor):
        """Zooms the view by a given factor, centered on the current view center."""
        new_scale = self.scale * factor
        new_scale = max(config.MIN_SCALE, min(config.MAX_SCALE, new_scale)) # Clamp scale

        # To zoom centered on the view, adjust offset
        # Currently, it zooms relative to the simulation origin (0,0) plus offset
        # For centered zoom on mouse cursor, would need mouse coords -> sim coords logic
        self.scale = new_scale
        # Simple zoom adjustment (may need refinement for true cursor centering)
        # print(f"Zoom: Scale={self.scale:.2f}") # Debug

    def reset_view(self):
        self.scale = config.INITIAL_SCALE
        self.offset_x = 0
        self.offset_y = 0
        logger.info("View reset to default.")

    def toggle_pause(self):
        """Toggles the simulation pause state."""
        self.paused = not self.paused
        status = "Paused" if self.paused else "Resumed"
        logger.info(f"Simulation {status}.")
        print(f"Simulation {status}") # Debug

    def change_speed(self):
        """Cycles through the predefined simulation speeds."""
        self.speed_modifier_index = (self.speed_modifier_index + 1) % len(config.SPEED_MODIFIERS)
        self.speed_modifier = config.SPEED_MODIFIERS[self.speed_modifier_index]
        logger.info(f"Simulation speed changed to: {self.speed_modifier}x")
        print(f"Simulation speed: {self.speed_modifier}x") # Debug

    def toggle_labels(self):
        """Toggles the visibility of celestial body labels."""
        self.show_labels = not self.show_labels
        status = "shown" if self.show_labels else "hidden"
        logger.info(f"Labels {status}.")
        print(f"Labels {status}") # Debug

    def toggle_orbits(self):
        """Toggles the visibility of orbits."""
        self.show_orbits = not self.show_orbits
        status = "shown" if self.show_orbits else "hidden"
        logger.info(f"Orbits {status}.")
        print(f"Orbits {status}") # Debug

    def _calculate_mst(self):
        """
        Calculates the Minimum Spanning Tree between satellites using Kruskal's algorithm,
        avoiding collisions with the sun and planets.
        """
        if not self.satellites:
            self.mst_edges = []
            return

        edges = []
        # 1. Generate potential edges between all pairs of satellites
        for i in range(len(self.satellites)):
            for j in range(i + 1, len(self.satellites)):
                sat1 = self.satellites[i]
                sat2 = self.satellites[j]
                p1 = sat1.get_sim_pos()
                p2 = sat2.get_sim_pos()
                dist = distance(p1, p2)

                # 2. Check for collisions with obstacles (Sun, Planets)
                collides = False
                for obstacle in self.obstacles:
                    obs_pos = obstacle.get_sim_pos()
                    obs_radius = obstacle.sim_radius
                    if line_segment_circle_collision(p1, p2, obs_pos, obs_radius):
                        collides = True
                        break # No need to check other obstacles for this edge

                if not collides:
                    edges.append((dist, sat1, sat2)) # Store distance and the satellite objects

        # 3. Sort edges by distance (weight)
        edges.sort()

        # 4. Apply Kruskal's algorithm using Union-Find
        uf = UnionFind(self.satellites) # Initialize UF with all satellites
        mst_result = []
        mst_cost = 0
        num_edges = 0

        for weight, u, v in edges:
            if uf.union(u, v): # If u and v are not already connected
                mst_result.append((u, v)) # Add edge (satellites themselves)
                mst_cost += weight
                num_edges += 1
                # Optimization: Stop when we have V-1 edges
                if num_edges == len(self.satellites) - 1:
                    break

        # Check if MST is connected (should be if graph was connected)
        # print(f"MST calculation complete. Edges: {len(mst_result)}, Cost: {mst_cost:.2f}, Sets remaining: {len(uf)}") # Debug
        self.mst_edges = mst_result

    def _find_path_on_mst(self, start_node, end_node):
        """
        Finds the unique path between two nodes on the MST using Breadth-First Search (BFS).
        Returns a list of Satellite objects representing the path, including start and end nodes.
        """
        if not self.mst_edges or start_node == end_node:
            return [start_node] if start_node == end_node else []

        # Build adjacency list representation of the MST
        adj = {sat: [] for sat in self.satellites}
        for u, v in self.mst_edges:
            adj[u].append(v)
            adj[v].append(u)

        queue = [(start_node, [start_node])] # (current_node, path_so_far)
        visited = {start_node}

        while queue:
            current_node, path = queue.pop(0)

            if current_node == end_node:
                return path # Path found

            for neighbor in adj.get(current_node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))

        return [] # Path not found (shouldn't happen on a connected MST)


    def update(self):
        """Main simulation loop update step."""
        current_time = time.time()
        # dt = (current_time - self.last_update_time) # Actual elapsed time - can be unstable
        dt = config.UPDATE_DELAY_MS / 1000.0 # Use fixed timestep for stability
        self.last_update_time = current_time

        if not self.paused:
            # 1. Update celestial body positions
            for body in self.celestial_bodies:
                body.update_position(dt, self.speed_modifier)

            # 2. Recalculate MST periodically
            if current_time - self.last_mst_recalculation_time > config.MST_RECALCULATION_INTERVAL_S:
                self._calculate_mst()
                self.last_mst_recalculation_time = current_time
                # print("Recalculated MST") # Debug

            # 3. Generate new data packets
            new_packets = []
            for satellite in self.satellites:
                packet = satellite.generate_data_packet(self.satellites, self.mst_edges)
                if packet:
                    # Find path for the new packet on the current MST
                    path_nodes = self._find_path_on_mst(packet.origin, packet.destination)
                    if path_nodes:
                        packet.set_path(path_nodes)
                        new_packets.append(packet)
                        logger.info(f"Packet {packet.id} generated: {packet.origin.name} -> {packet.destination.name} (Path length: {len(path_nodes)})")
                        #print(f"Generated packet {packet.id}: {packet.origin.name} -> {packet.destination.name}") # Debug
                    else:
                         logger.warning(f"Packet {packet.id} generated but no path found on MST: {packet.origin.name} -> {packet.destination.name}")
                         #print(f"Packet {packet.id} generated but no path found.") # Debug


            self.data_packets.extend(new_packets)

            # 4. Update data packet positions
            packets_to_remove = []
            for packet in self.data_packets:
                packet.update_position(dt, self.speed_modifier)
                if packet.reached_destination:
                    packets_to_remove.append(packet)

            # 5. Remove packets that reached their destination
            for packet in packets_to_remove:
                packet.delete_graphics(self.canvas) # Clean up canvas element
                self.data_packets.remove(packet)


        # 6. Draw everything
        self.draw()

        # Schedule the next update
        self.canvas.after(config.UPDATE_DELAY_MS, self.update)

    def _draw_mst(self):
        """Draws the calculated MST edges."""
        # Clear previous MST lines
        for line_id in self.mst_lines:
            self.canvas.delete(line_id)
        self.mst_lines.clear()

        if not self.mst_edges:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        for sat1, sat2 in self.mst_edges:
            x1_sim, y1_sim = sat1.get_sim_pos()
            x2_sim, y2_sim = sat2.get_sim_pos()

            x1_can, y1_can = transform_coords(x1_sim, y1_sim, canvas_width, canvas_height, self.scale, self.offset_x, self.offset_y)
            x2_can, y2_can = transform_coords(x2_sim, y2_sim, canvas_width, canvas_height, self.scale, self.offset_x, self.offset_y)

            line_id = self.canvas.create_line(
                x1_can, y1_can, x2_can, y2_can,
                fill=config.MST_EDGE_COLOR,
                width=config.MST_LINE_WIDTH,
                tags="mst_edge"
            )
            self.mst_lines.append(line_id)

    def draw(self):
        """Clears the canvas and redraws all simulation elements."""
        # More efficient redraw (update coords) is done in individual draw methods
        # Here we just ensure things are layered correctly and MST is redrawn
        # self.canvas.delete("all") # Avoid deleting everything if possible

        # Draw celestial bodies (planets update their own orbits/labels)
        for body in self.celestial_bodies:
            body.draw(self.canvas, self.scale, self.offset_x, self.offset_y, self.show_labels, self.show_orbits)

        # Draw MST edges
        self._draw_mst()

        # Draw data packets
        for packet in self.data_packets:
            packet.draw(self.canvas, self.scale, self.offset_x, self.offset_y)

        # Ensure certain elements are drawn on top (optional)
        self.canvas.tag_raise("celestial_body")
        self.canvas.tag_raise("data_packet")
        self.canvas.tag_raise("label")

        # Update the canvas display
        # self.canvas.update_idletasks() # May not be necessary with after loop

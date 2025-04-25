# utils.py
import math

class UnionFind:
    """
    Weighted Quick Union with Path Compression implementation of Union-Find.
    Elements can be any hashable type.
    """
    def __init__(self, elements=None):
        self.parent = {}  # Stores parent of each element
        self.size = {}    # Stores size of the subtree rooted at each element
        self.num_sets = 0 # Number of disjoint sets
        if elements:
            for element in elements:
                self.add(element)

    def add(self, element):
        """Add a new element as a singleton set."""
        if element not in self.parent:
            self.parent[element] = element
            self.size[element] = 1
            self.num_sets += 1

    def find(self, element):
        """Find the representative (root) of the set containing element, with path compression."""
        if element not in self.parent:
            self.add(element) # Add element if it doesn't exist
            return element

        # Path compression
        root = element
        while root != self.parent[root]:
            root = self.parent[root]

        # Compress the path
        current = element
        while current != root:
            next_parent = self.parent[current]
            self.parent[current] = root
            current = next_parent

        return root

    def union(self, element1, element2):
        """Merge the sets containing element1 and element2 using union by size."""
        root1 = self.find(element1)
        root2 = self.find(element2)

        if root1 != root2:
            # Union by size: attach smaller tree to larger tree
            if self.size[root1] < self.size[root2]:
                self.parent[root1] = root2
                self.size[root2] += self.size[root1]
            else:
                self.parent[root2] = root1
                self.size[root1] += self.size[root2]
            self.num_sets -= 1
            return True # Union successful
        return False # Elements already in the same set

    def connected(self, element1, element2):
        """Check if element1 and element2 are in the same set."""
        return self.find(element1) == self.find(element2)

    def __len__(self):
        """Return the number of disjoint sets."""
        return self.num_sets

    def __contains__(self, element):
        return element in self.parent

def distance(p1, p2):
    """Calculate Euclidean distance between two points (x, y)."""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def closest_point_on_segment(seg_p1, seg_p2, point):
    """Find the point on the line segment [seg_p1, seg_p2] closest to 'point'."""
    seg_vec = (seg_p2[0] - seg_p1[0], seg_p2[1] - seg_p1[1])
    pt_vec = (point[0] - seg_p1[0], point[1] - seg_p1[1])

    seg_len_sq = seg_vec[0]**2 + seg_vec[1]**2
    if seg_len_sq == 0: # Segment is a point
        return seg_p1

    # Project pt_vec onto seg_vec
    dot_product = pt_vec[0] * seg_vec[0] + pt_vec[1] * seg_vec[1]
    t = max(0, min(1, dot_product / seg_len_sq)) # Clamp t to [0, 1]

    closest_pt = (seg_p1[0] + t * seg_vec[0], seg_p1[1] + t * seg_vec[1])
    return closest_pt

def line_segment_circle_collision(p1, p2, circle_center, circle_radius):
    """
    Check if a line segment [p1, p2] intersects with a circle.
    Returns True if collision occurs, False otherwise.
    """
    # 1. Check if either endpoint is inside the circle
    if distance(p1, circle_center) <= circle_radius:
        return True
    if distance(p2, circle_center) <= circle_radius:
        return True

    # 2. Find the closest point on the line segment to the circle's center
    closest_pt = closest_point_on_segment(p1, p2, circle_center)

    # 3. Check if the distance from the closest point to the center is less than the radius
    dist_sq = (closest_pt[0] - circle_center[0])**2 + (closest_pt[1] - circle_center[1])**2
    if dist_sq <= circle_radius**2:
        return True

    return False

def transform_coords(sim_x, sim_y, canvas_width, canvas_height, scale, offset_x, offset_y):
    """Convert simulation coordinates to canvas coordinates."""
    center_x = canvas_width / 2
    center_y = canvas_height / 2
    canvas_x = center_x + (sim_x * scale) + offset_x
    canvas_y = center_y + (sim_y * scale) + offset_y
    return canvas_x, canvas_y

def reverse_transform_coords(canvas_x, canvas_y, canvas_width, canvas_height, scale, offset_x, offset_y):
    """Convert canvas coordinates back to simulation coordinates."""
    center_x = canvas_width / 2
    center_y = canvas_height / 2
    sim_x = (canvas_x - center_x - offset_x) / scale
    sim_y = (canvas_y - center_y - offset_y) / scale
    return sim_x, sim_y

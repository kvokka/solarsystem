# main.py
import tkinter as tk
from simulation import Simulation
import config
from logger_setup import logger # Ensure logger is initialized

def main():
    """Sets up the Tkinter window and starts the simulation."""
    root = tk.Tk()
    root.title("Solar System Simulation")

    # Attempt to center the window (may depend on OS window manager)
    window_width = config.WINDOW_WIDTH
    window_height = config.WINDOW_HEIGHT
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width / 2)
    center_y = int(screen_height/2 - window_height / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Create the canvas for drawing
    canvas = tk.Canvas(root, bg=config.BG_COLOR, highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    # Initialize and start the simulation
    sim = Simulation(canvas)
    # Need to delay the first update slightly to allow canvas size to be determined
    root.after(100, sim.update)

    # Handle window closing
    def on_closing():
        logger.info("Simulation window closed.")
        print("Exiting simulation...")
        # Perform any cleanup here if needed
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    main()

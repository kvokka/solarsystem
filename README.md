# Solar System Simulation

Generated with [Gemini 2.5 pro](https://aistudio.google.com/app/prompts?state=%7B%22ids%22:%5B%221aESAcQopv5MtuehnahrdVi03s-K6vaci%22%5D,%22action%22:%22open%22,%22userId%22:%22104869750760996850676%22,%22resourceKeys%22:%7B%7D%7D&usp=sharing)

It's a reply to <https://github.com/Katan3615/solarsystem>

## Description

This project is an interactive simulation of a simplified Solar System using Python and Tkinter. It includes planets orbiting the sun, satellites orbiting planets, and dynamic data packets traveling between satellites via the shortest available paths on a Minimum Spanning Tree (MST). The simulation includes collision-aware MST calculation and visualization of the dynamic communication network.

## Key Features

- Real-time animation of celestial objects.
- Orbiting planets and satellites.
- Data packet generation from satellites and transfer across the network via MST paths.
- Dynamic computation and drawing of the MST between satellites, avoiding planet/sun collisions.
- Simulation control: Pause/Resume and adjustable speed.
- View controls: Zoom and Pan.
- Display toggles: Labels and Orbits.
- Detailed logging of simulation events to `log.txt`.

## Requirements

- Python 3.8+
- Tkinter (usually included by default with Python)

## To Run

1. Save all the provided Python files (`main.py`, `simulation.py`, `celestial_body.py`, `data_packet.py`, `utils.py`, `logger_setup.py`, `config.py`) in the same directory.
2. Open a terminal or command prompt in that directory.
3. Run the command:

   ```bash
   python main.py

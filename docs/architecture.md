
# Stellar Architecture

<!--toc:start-->
- [Stellar Architecture](#stellar-architecture)
  - [Overview](#overview)
  - [Project Structure](#project-structure)
  - [`interfaces/`](#interfaces)
    - [Components in the interfaces/ folder](#components-in-the-interfaces-folder)
      - [1. window_interface.py](#1-windowinterfacepy)
      - [2. renderer_interface.py](#2-rendererinterfacepy)
      - [3. input_interface.py](#3-inputinterfacepy)
  - [Modular Design](#modular-design)
  - [Adding New Implementations](#adding-new-implementations)
  - [Additional Notes](#additional-notes)
<!--toc:end-->

## Overview

This document explains the architecture of the terminal emulator project, including the role of each component and how they interact to form a modular and extensible system.

---

## Project Structure

The project is organized into several distinct modules, each of which is responsible for a specific aspect of the terminal emulator. Below is a breakdown of each module:

```text
stellar/
│
├── stellar/
│   ├── main.py
│   ├── config.py
│   ├── interfaces/
│   ├── engines/
│   ├── renderer/
│   ├── input/
│   ├── utils/
│
├── tests/
├── docs/
├── requirements.txt
└── setup.py
```

## `interfaces/`

The interfaces/ folder contains abstract base classes (ABCs) that define the contracts for key components of the system. By adhering to these contracts, we ensure that each implementation can be easily swapped or extended without affecting the rest of the system. This is crucial for maintaining modularity and allowing us to replace different components (like window engines or renderers) if necessary.

### Components in the interfaces/ folder

#### 1. window_interface.py

This file defines the WindowInterface class, which serves as a contract for windowing systems. Any windowing engine (e.g., Tkinter, PyQt, Pygame) must implement this interface to ensure compatibility with the rest of the terminal emulator.

Example Methods

create_window(title: str, width: int, height: int): Initializes a window with the specified title and dimensions.
draw_rectangle(x1: int, y1: int, x2: int, y2: int, color: str): Draws a rectangle on the window.
handle_events(): Handles window events like resizing or closing.
run(): Starts the window's main event loop.

#### 2. renderer_interface.py

This file defines the RendererInterface class, which outlines the methods necessary for rendering text and UI elements. This enables us to use different rendering backends like a default renderer, ncurses, or others.

Example Methods
draw_text(text: str, x: int, y: int): Renders text at the specified coordinates.
clear_screen(): Clears the window or terminal screen.
update_screen(): Refreshes the screen to display updated content.

#### 3. input_interface.py

This file defines the InputInterface, which governs how input is captured from users. This includes handling keyboard and mouse inputs. By abstracting input handling, different input sources (e.g., physical keyboard, virtual keyboard, etc.) can be easily integrated.

Example Methods
capture_keypress(): Captures a key press event.
capture_mouse_event(): Handles mouse events (if required by the UI).

## Modular Design

The separation of concerns between windowing, rendering, and input handling ensures that we can easily switch or add components. For example, if you want to replace the Tkinter windowing engine with PyQt, all you need to do is implement the WindowInterface for PyQt and update the configuration.

## Adding New Implementations
If you want to add a new engine or renderer in the future, follow these steps:

1. Create a new implementation of the desired interface (WindowInterface, RendererInterface, etc.) in the appropriate folder (engines/, renderer/).
2. Register the new implementation in the config.py file or through a factory pattern in main.py.
3. Ensure that the new implementation adheres to the interface's contract so that it integrates smoothly into the rest of the system.

## Additional Notes

- This file helps guide new developers and contributors to the project, explaining the reasoning behind using interfaces and how to extend the system with new implementations.
- You can update this file as the architecture evolves or when new engines are added.

Let me know if you'd like more details in the file or additional sections for other parts of the project!

import math

import customtkinter


class VolumeVisualizer(customtkinter.CTkFrame):
    """
    A CustomTkinter widget to visualize audio volume as a vertical dotted line.

    The volume is represented by highlighting a percentage of the dots.
    This widget is dynamically resizable.
    """

    def __init__(
        self,
        master,
        width: int = 0,
        height: int = 100,
        dot_radius: int = 4,
        dot_spacing: int = 2,
        bg=0,
        active_dot_color="#2ECC71",
        inactive_dot_color="#A2A2A2",
        **kwargs,
    ):
        """
        Initializes the VolumeVisualizer widget.

        Args:
            master: The parent widget.
            width (int): The initial width of the visualizer frame.
            height (int): The initial height of the visualizer frame.
            number_of_dots (int): The total number of dots to display.
            **kwargs: Additional keyword arguments for CTkFrame.
        """
        super().__init__(
            master,
            width=width if width != 0 else 2 * dot_radius,
            height=height,
            **kwargs,
        )

        self.dot_radius = dot_radius  # Radius of each circle/dot
        self.dot_spacing = dot_spacing  # Spacing between dots
        self._current_volume = 0.0  # Store the current volume to re-apply on resize
        self.bg = bg
        self.active_dot_color = active_dot_color
        self.inactive_dot_color = inactive_dot_color

        # Create a canvas to draw the dots
        self.canvas = customtkinter.CTkCanvas(
            self,
            bg=(
                self.bg
                if self.bg != 0
                else self._apply_appearance_mode(
                    customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
                )
            ),
            highlightthickness=0,  # Remove canvas border
            width=2 * self.dot_radius + 2,
        )
        self.canvas.pack(fill="y", expand=True)

        self.dot_ids = []  # To store canvas item IDs for each dot

        # Bind the <Configure> event to the canvas for dynamic resizing
        # This will call _on_resize whenever the canvas size changes
        self.canvas.bind("<Configure>", self._on_resize)

        # Initial draw of dots (will be triggered by the first <Configure> event too,
        # but good to have a direct call for immediate display if needed)
        # We call it after binding to ensure the event handler is set up.
        # The _on_resize will handle the actual drawing.
        # self._redraw_dots() # This will be implicitly called by the first <Configure> event

    def _on_resize(self, event=None):
        """
        Handles the resizing of the canvas and redraws the dots.
        This method is called when the <Configure> event is triggered.
        """
        self._redraw_dots()
        # After redrawing, re-apply the current volume to update dot colors
        self.set_volume(self._current_volume)

    def _redraw_dots(self):
        """
        Redraws all the dots based on the current canvas size.
        This method is called on initialization and whenever the widget is resized.
        """
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # If canvas_width or canvas_height are 0 (e.g., before packing/display),
        # use the initial dimensions from the frame or return early.
        if canvas_width == 0 or canvas_height == 0:
            return

        # Clear existing dots before redrawing
        for dot_id in self.dot_ids:
            self.canvas.delete(dot_id)
        self.dot_ids.clear()

        # Calcualte number of dots
        required_height_per_dot = 2 * self.dot_radius + self.dot_spacing
        self.number_of_dots = math.floor(
            (canvas_height / required_height_per_dot) - self.dot_spacing
        )

        total_required_height = (
            self.number_of_dots * required_height_per_dot - self.dot_spacing
        )

        # Calculate vertical space available for dots
        # Ensure there's enough space for all dots
        if self.number_of_dots > 0:
            # Adjust dot spacing if total required height exceeds canvas height
            if total_required_height > canvas_height:
                # Calculate new spacing to fit all dots
                effective_dot_height = canvas_height / self.number_of_dots
                self.dot_spacing = max(0, effective_dot_height - (2 * self.dot_radius))
                total_required_height = (
                    self.number_of_dots * (2 * self.dot_radius + self.dot_spacing)
                    - self.dot_spacing
                )
            else:
                pass

            # Calculate start Y position to center the dots vertically
            centering = (canvas_height - total_required_height) / 2
            start_y = centering if centering >= self.dot_radius else self.dot_radius

            center_x = canvas_width / 2

            # Draw dots from bottom to top (representing 0% to 100%)
            for i in range(self.number_of_dots):
                # Calculate y-coordinate for the current dot
                # Dots are drawn from bottom up, so higher index means higher volume
                y = start_y + (self.number_of_dots - 1 - i) * (
                    2 * self.dot_radius + self.dot_spacing
                )

                x1 = center_x - self.dot_radius
                y1 = y - self.dot_radius
                x2 = center_x + self.dot_radius
                y2 = y + self.dot_radius

                dot_id = self.canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=self.inactive_dot_color,
                    outline="",  # No outline
                )
                self.dot_ids.append(dot_id)

        else:
            pass

    def set_volume(self, volume: float):
        """
        Sets the volume level and updates the visualizer.

        Args:
            volume (float): The volume level, a float between 0.0 and 1.0.
                            0.0 means 0% volume, 1.0 means 100% volume.
        """
        if not (0.0 <= volume <= 1.0):
            print("Warning: Volume must be between 0.0 and 1.0. Clamping value.")
            volume = max(0.0, min(1.0, volume))

        self._current_volume = volume  # Store for redraws

        if not self.dot_ids:  # Ensure dots have been drawn before trying to color them
            return

        # Calculate how many dots should be highlighted
        highlight_count = math.ceil(volume * self.number_of_dots)

        # Define colors for highlighted and unhighlighted dots
        highlight_color = self.active_dot_color
        default_color = self.inactive_dot_color

        # Iterate through dots and set their color
        # Remember: dots are stored from bottom (index 0) to top (last index)
        for i, dot_id in enumerate(self.dot_ids):
            if i < highlight_count:
                # Highlight dots from the bottom up
                self.canvas.itemconfig(dot_id, fill=highlight_color)
            else:
                # Unhighlight remaining dots
                self.canvas.itemconfig(dot_id, fill=default_color)

        # Redraw the canvas to reflect changes
        self.canvas.update_idletasks()


# --- Example Usage (Simplified for app integration) ---
if __name__ == "__main__":
    customtkinter.set_appearance_mode(
        "System"
    )  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme(
        "blue"
    )  # Themes: "blue" (default), "dark-blue", "green"

    app = customtkinter.CTk()
    app.title("Volume Visualizer Demo (Resizable)")
    app.geometry("500x500")

    # Create a main frame to hold the visualizer and allow it to expand
    main_frame = customtkinter.CTkFrame(app, fg_color="transparent", width=10)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Create the VolumeVisualizer widget
    # It will expand to fill the main_frame
    volume_visualizer = VolumeVisualizer(
        master=main_frame,
        corner_radius=15,  # Add some rounded corners to the frame
    )
    # Use pack with expand=True to make it fill available space in main_frame
    volume_visualizer.pack(pady=10, padx=10, fill="both", expand=True)

    # Example of how you would set the volume in your app
    # You can call this method from anywhere in your application logic
    initial_volume = 0.75  # 75% volume
    volume_visualizer.set_volume(initial_volume)

    # Add a button to demonstrate changing volume
    def change_volume_demo():
        current_vol = volume_visualizer._current_volume
        new_vol = (current_vol + 0.1) % 1.1  # Cycle volume from 0 to 1.0
        if new_vol > 1.0:  # Ensure it wraps around correctly
            new_vol = 0.0
        volume_visualizer.set_volume(new_vol)

    change_button = customtkinter.CTkButton(
        master=app, text="Change Volume", command=change_volume_demo
    )
    change_button.pack(pady=10)

    app.mainloop()

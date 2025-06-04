import tkinter as tk

import customtkinter


class CustomTkButtonWidget(customtkinter.CTkFrame):
    """
    A custom button widget for customtkinter with an active indicator on the left
    and an identity indicator at the bottom right.

    Attributes:
        command (callable): The function to call when the button is clicked.
        _active_indicator_color (str): The current color of the active indicator.
        _identity_indicator_color (str): The current color of the identity indicator.
        active_indicator (customtkinter.CTkFrame): The frame representing the active indicator.
        button_label (customtkinter.CTkLabel): The label displaying the button's text.
        identity_indicator (customtkinter.CTkFrame): The frame representing the identity indicator.
    """

    def __init__(
        self,
        master,
        text="Button",
        command=None,
        active_indicator_color="green",
        identity_indicator_color="red",
        width=160,
        height=90,
        corner_radius=10,
        bg_color="transparent",
        fg_color="gray20",
        hover_color="gray15",
        text_color="white",
        font_size=18,
        font_weight="bold",
        **kwargs,
    ):
        """
        Initializes the CustomTkButtonWidget.

        Args:
            master (tkinter.Tk or customtkinter.CTk or customtkinter.CTkFrame):
                The parent widget.
            text (str): The text to display on the button.
            command (callable, optional): The function to execute when the button is clicked.
            active_indicator_color (str): The initial color of the active indicator.
            identity_indicator_color (str): The initial color of the identity indicator.
            width (int): The width of the overall custom button widget.
            height (int): The height of the overall custom button widget.
            corner_radius (int): The corner radius for the overall button and active indicator.
            bg_color (str): The background color of the parent widget (for transparent blending).
            fg_color (str): The foreground color of the custom button (its main background).
            text_color (str): The color of the button's text.
            font_size (int): The font size of the button's text.
            font_weight (str): The font weight of the button's text (e.g., "normal", "bold").
            **kwargs: Additional keyword arguments to pass to customtkinter.CTkFrame.
        """
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            bg_color=bg_color,
            fg_color=fg_color,
            **kwargs,
        )

        self._width = width
        self._height = height

        self.command = command
        self._active_indicator_color = active_indicator_color
        self._identity_indicator_color = identity_indicator_color
        self.fg_color = fg_color
        self.hover_color = hover_color

        self.grid_propagate(False)

        # Configure grid for the CustomTkButtonWidget (the main frame)
        # Column 0 for the active indicator (fixed width)
        self.grid_columnconfigure(0, weight=0)
        # Column 1 for the main button text content (expands to fill space)
        self.grid_columnconfigure(1, weight=1)
        # Single row that expands to fill height
        self.grid_rowconfigure(0, weight=1)

        # Active Indicator (left bar)
        self.active_indicator = customtkinter.CTkFrame(
            self,
            width=15,  # Fixed width for the indicator bar
            height=height - 10,  # Bcs this shit is bugging
            corner_radius=self.cget(
                "corner_radius"
            ),  # Match parent's corner radius for top/bottom
            fg_color=self._active_indicator_color,
            bg_color="transparent",  # Ensures it blends with the parent's background
        )
        # Place the active indicator in the first column, sticky "ns" to fill height
        # padx/pady add internal spacing from the frame's edges
        self.active_indicator.grid(row=0, column=0, sticky="ns", padx=(5, 0), pady=5)

        # Button Text Label
        self.button_label = customtkinter.CTkLabel(
            self,
            text=text,
            text_color=text_color,
            font=customtkinter.CTkFont(size=font_size, weight=font_weight),
        )
        # Place the label in the second column, sticky "nsew" to fill available space
        self.button_label.grid(row=0, column=1, sticky="nsew", padx=(10, 10), pady=5)

        # Identity Indicator (bottom right circular rectangle)
        self.identity_indicator = customtkinter.CTkFrame(
            self,
            width=40,  # Fixed width for the indicator
            height=15,  # Fixed height for the indicator
            corner_radius=7,  # Half of height (15/2 = 7.5) for a more circular end look
            fg_color=self._identity_indicator_color,
            bg_color="transparent",  # Ensures it blends with the parent's background
        )
        # Use the place manager to position it relative to the main CustomTkButtonWidget frame.
        # relx=0.95 means 95% from the left edge of the parent.
        # rely=0.90 means 90% from the top edge of the parent.
        # anchor="se" means the southeast corner of the identity_indicator is placed at (relx, rely).
        self.identity_indicator.place(relx=0.95, rely=0.90, anchor="se")

        # Bind click events to the entire frame and its children to ensure the whole
        # custom widget is clickable.
        self.bind("<Button-1>", self._on_click)
        self.active_indicator.bind("<Button-1>", self._on_click)
        self.button_label.bind("<Button-1>", self._on_click)
        self.identity_indicator.bind("<Button-1>", self._on_click)

        # Bind hover events for visual feedback
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.active_indicator.bind("<Enter>", self._on_enter)
        self.active_indicator.bind("<Leave>", self._on_leave)
        self.button_label.bind("<Enter>", self._on_enter)
        self.button_label.bind("<Leave>", self._on_leave)
        self.identity_indicator.bind("<Enter>", self._on_enter)
        self.identity_indicator.bind("<Leave>", self._on_leave)

    def _on_click(self, event=None):
        """Internal method to handle click events and execute the command."""
        if self.command:
            self.command()

    def _on_enter(self, event=None):
        """Internal method to handle mouse entering the widget, changing its background."""
        self.configure(fg_color=self.hover_color)  # KJKJKJKJKJK

    def _on_leave(self, event=None):
        """Internal method to handle mouse leaving the widget, reverting its background."""
        self.configure(fg_color=self.fg_color)  # Revert to original

    def set_active_indicator_color(self, color):
        """Sets the color of the active indicator."""
        self.active_indicator.configure(fg_color=color)
        self._active_indicator_color = color

    def get_active_indicator_color(self):
        """Returns the current color of the active indicator."""
        return self._active_indicator_color

    def set_identity_indicator_color(self, color):
        """Sets the color of the identity indicator."""
        self.identity_indicator.configure(fg_color=color)
        self._identity_indicator_color = color

    def get_identity_indicator_color(self):
        """Returns the current color of the identity indicator."""
        return self._identity_indicator_color

    def set_text(self, text):
        """Sets the text displayed on the button."""
        self.button_label.configure(text=text)

    def get_text(self):
        """Returns the current text displayed on the button."""
        return self.button_label.cget("text")

    def set_command(self, command):
        """Sets the command function to be executed on button click."""
        self.command = command


# --- Example Usage ---
if __name__ == "__main__":
    # Set the appearance mode and default color theme for customtkinter
    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("blue")

    # Create the main application window
    app = customtkinter.CTk()
    app.title("Custom Button Widget Example")
    app.geometry("800x600")

    # Configure the grid for the main app window to center widgets
    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)  # For the first button
    app.grid_rowconfigure(1, weight=1)  # For the toggle button
    app.grid_rowconfigure(2, weight=1)  # For the second custom button

    # Define a command function for the first custom button
    def on_my_button_click():
        print("My Custom Button clicked!")
        # Example: Change button text after click
        my_button.set_text("Clicked!")

    # Create an instance of the custom button
    my_button = CustomTkButtonWidget(
        master=app,
        text="My Custom Button",
        command=on_my_button_click,
        width=350,  # Overall width of the custom button
        height=500,  # Overall height of the custom button
        corner_radius=15,  # Corner radius for the main button frame
        fg_color="gray17",  # Background color of the overall button
        active_indicator_color="lime",  # Initial color for the active indicator
        identity_indicator_color="orange",  # Initial color for the identity indicator
    )
    # Place the button in the center of the window
    my_button.place(relx=0.5, rely=0.3, anchor="center")

    # Define a function to demonstrate changing indicator colors
    def toggle_colors():
        current_active_color = my_button.get_active_indicator_color()
        current_identity_color = my_button.get_identity_indicator_color()

        # Toggle active indicator color between lime and red
        new_active_color = "red" if current_active_color == "lime" else "lime"
        # Toggle identity indicator color between orange and blue
        new_identity_color = "blue" if current_identity_color == "orange" else "orange"

        my_button.set_active_indicator_color(new_active_color)
        my_button.set_identity_indicator_color(new_identity_color)
        print(f"Changed active to {new_active_color}, identity to {new_identity_color}")

    # Create a standard CTkButton to trigger color changes on the custom button
    change_button = customtkinter.CTkButton(
        master=app,
        text="Toggle Indicator Colors",
        command=toggle_colors,
        width=200,
        height=40,
        corner_radius=10,
        fg_color="blue",
        hover_color="darkblue",
    )
    change_button.place(relx=0.5, rely=0.6, anchor="center")

    # Create another custom button instance with different initial colors
    def on_another_button_click():
        print("Another button clicked!")
        another_button.set_text("Another Clicked!")

    another_button = CustomTkButtonWidget(
        master=app,
        text="Another Button",
        command=on_another_button_click,
        width=350,
        height=90,
        corner_radius=15,
        fg_color="gray17",
        active_indicator_color="cyan",
        identity_indicator_color="purple",
    )
    another_button.place(relx=0.5, rely=0.8, anchor="center")

    # Start the customtkinter event loop
    app.mainloop()

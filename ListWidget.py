import customtkinter


class ListWidget(customtkinter.CTkScrollableFrame):
    """
    A CustomTkinter widget that displays a scrollable list of customizable buttons
    arranged in a grid layout with a configurable number of columns.
    """

    def __init__(self, master, columns: int = 1, **kwargs):
        """
        Initializes the ListWidget.

        Args:
            master: The parent widget.
            columns (int): The number of columns for the grid layout.
                           Must be at least 1.
            **kwargs: Additional keyword arguments for CTkScrollableFrame.
                      (e.g., width, height, fg_color, scrollbar_button_color)
        """
        if columns < 1:
            raise ValueError("Number of columns must be at least 1.")

        super().__init__(master, **kwargs)

        self.columns = columns
        self._buttons = []  # Stores references to the CTkButton instances
        self._current_row = 0
        self._current_column = 0

        # For debouncing scroll events
        self._scroll_job_id = None
        self._scroll_delay_ms = 10  # Milliseconds delay for debouncing

        # For smooth animation
        self._animation_job_id = None
        self._animation_duration_ms = 150  # Total duration of the scroll animation
        self._animation_steps = 10  # Number of steps in the animation
        self._current_animation_step = 0
        self._scroll_start_y = 0.0  # Start scroll position (0.0 to 1.0)
        self._scroll_target_y = 0.0  # Target scroll position (0.0 to 1.0)

        # Configure grid weights to make columns expand proportionally
        for i in range(self.columns):
            self.grid_columnconfigure(i, weight=1)

        # Bind mouse wheel events for scrolling
        self._bind_mouse_wheel_scroll()

    def _bind_mouse_wheel_scroll(self):
        """
        Binds mouse wheel events to the internal canvas of the scrollable frame
        and its children to enable scrolling with the mouse wheel.
        """
        # Bind to the internal canvas of CTkScrollableFrame
        if hasattr(
            self, "_parent_canvas"
        ):  # Ensure _parent_canvas exists before binding
            self._parent_canvas.bind(
                "<MouseWheel>", self._on_mouse_wheel
            )  # Windows/macOS
            self._parent_canvas.bind(
                "<Button-4>", self._on_mouse_wheel
            )  # Linux scroll up
            self._parent_canvas.bind(
                "<Button-5>", self._on_mouse_wheel
            )  # Linux scroll down

        # Also bind to the inner frame where the widgets are placed
        if hasattr(self, "_parent_frame"):  # Ensure _parent_frame exists
            self._parent_frame.bind("<MouseWheel>", self._on_mouse_wheel)
            self._parent_frame.bind("<Button-4>", self._on_mouse_wheel)
            self._parent_frame.bind("<Button-5>", self._on_mouse_wheel)

        # Recursively bind to all children of the inner frame (the buttons themselves)
        self.bind_all("<MouseWheel>", self._on_mouse_wheel)
        self.bind_all("<Button-4>", self._on_mouse_wheel)
        self.bind_all("<Button-5>", self._on_mouse_wheel)

    def _on_mouse_wheel(self, event):
        """
        Handles mouse wheel events to scroll the content with debouncing and smooth animation.
        """
        # Cancel any pending debounced scroll job
        if self._scroll_job_id:
            self.after_cancel(self._scroll_job_id)

        # Determine scroll direction and calculate target scroll units
        scroll_direction = 0
        if event.num == 4 or event.delta > 0:  # Scroll up
            scroll_direction = -1
        elif event.num == 5 or event.delta < 0:  # Scroll down
            scroll_direction = 1

        if scroll_direction != 0:
            # Schedule the actual scroll action after a short debounce delay
            self._scroll_job_id = self.after(
                self._scroll_delay_ms,
                lambda: self._initiate_smooth_scroll(scroll_direction),
            )

        # Prevent event propagation
        return "break"

    def _initiate_smooth_scroll(self, direction):
        """
        Calculates the target scroll position and starts the smooth animation.
        """
        if not hasattr(self, "_parent_canvas"):
            return

        # Get current scroll position (as a fraction from 0.0 to 1.0)
        # yview() returns (start_fraction, end_fraction)
        current_y_fraction = self._parent_canvas.yview()[0]

        # Calculate the approximate height of one "unit" (e.g., one row of buttons)
        # This is an approximation. A more precise calculation would involve
        # summing actual button heights and paddings.
        # For now, we'll use a fixed step size relative to the scrollable area.
        scroll_step_fraction = (
            0.05  # Scroll 5% of the total scrollable height per wheel tick
        )

        # Calculate the target scroll position
        target_y_fraction = current_y_fraction + (direction * scroll_step_fraction)

        # Clamp the target position between 0.0 (top) and 1.0 (bottom)
        self._scroll_target_y = max(0.0, min(1.0, target_y_fraction))
        self._scroll_start_y = current_y_fraction
        self._current_animation_step = 0

        # Cancel any ongoing animation before starting a new one
        if self._animation_job_id:
            self.after_cancel(self._animation_job_id)

        # Start the animation
        self._animate_scroll()

    def _animate_scroll(self):
        """
        Performs one step of the smooth scrolling animation.
        """
        if not hasattr(self, "_parent_canvas"):
            return

        if self._current_animation_step < self._animation_steps:
            # Calculate the current position using linear interpolation
            t = self._current_animation_step / self._animation_steps
            # You could use an easing function here for more advanced effects, e.g.:
            # t = t * t * (3 - 2 * t) # ease-in-out cubic

            current_animated_y = (
                self._scroll_start_y
                + (self._scroll_target_y - self._scroll_start_y) * t
            )

            self._parent_canvas.yview_moveto(current_animated_y)
            self._current_animation_step += 1

            # Schedule the next animation step
            step_delay = self._animation_duration_ms // self._animation_steps
            self._animation_job_id = self.after(step_delay, self._animate_scroll)
        else:
            # Animation finished, ensure it's at the exact target position
            self._parent_canvas.yview_moveto(self._scroll_target_y)
            self._animation_job_id = None  # Clear the job ID

    def add_button(self, text: str, command=None, **button_kwargs):
        """
        Adds a new customizable button to the list.

        The button will be placed in the next available grid cell.
        If the current row is full, a new row will be started.

        Args:
            text (str): The text to display on the button.
            command (callable, optional): The function to call when the button is clicked.
                                          Defaults to None.
            **button_kwargs: Additional keyword arguments to customize the CTkButton.
                             These are passed directly to the CTkButton constructor.
                             Examples: fg_color, text_color, hover_color, font, image,
                                       width, height, corner_radius, border_width, etc.
        Returns:
            customtkinter.CTkButton: The created button instance.
        """
        # Create the button with provided arguments
        button = customtkinter.CTkButton(
            master=self,  # Master is the CTkScrollableFrame itself, which means it's placed in _parent_frame
            text=text,
            command=command,
            **button_kwargs,
        )

        # Place the button in the grid
        button.grid(
            row=self._current_row,
            column=self._current_column,
            padx=5,  # Small padding around each button
            pady=5,
            sticky="nsew",  # Make buttons expand to fill their grid cell
        )

        self._buttons.append(button)

        # Update the current column and row for the next button
        self._current_column += 1
        if self._current_column >= self.columns:
            self._current_column = 0
            self._current_row += 1

        return button

    def clear_buttons(self):
        """
        Removes all buttons from the widget.
        """
        for button in self._buttons:
            button.destroy()  # Destroy the tkinter widget
        self._buttons.clear()  # Clear the list of references
        self._current_row = 0
        self._current_column = 0

    def get_buttons(self):
        """
        Returns a list of all CTkButton instances currently in the widget.
        """
        return self._buttons


# --- Example Usage ---
if __name__ == "__main__":
    customtkinter.set_appearance_mode(
        "System"
    )  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme(
        "blue"
    )  # Themes: "blue" (default), "dark-blue", "green"

    app = customtkinter.CTk()
    app.title("Scrollable Button List Demo (Smooth Scroll)")
    app.geometry("800x600")

    # Configure grid for the main app window to allow the widget to expand
    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    # --- Example 1: 2 Columns ---
    print("--- Creating ListWidget with 2 columns ---")
    button_list_2_cols = ListWidget(
        master=app,
        columns=2,
        width=350,  # Set an initial width
        height=400,  # Set an initial height
        fg_color=(
            "gray80",
            "gray20",
        ),  # Custom background color for the scrollable frame
        corner_radius=10,
        scrollbar_button_color="green",
        scrollbar_button_hover_color="darkgreen",
    )
    button_list_2_cols.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def button_action(button_name):
        print(f"Button '{button_name}' clicked!")

    # Add 40 buttons to demonstrate scrolling and grid layout
    for i in range(1, 61):  # Increased number of buttons for better scroll demo
        button_list_2_cols.add_button(
            text=f"Item {i}",
            command=lambda i=i: button_action(f"Item {i}"),
            fg_color="blue",
            hover_color="darkblue",
            text_color="white",
            height=50,
            corner_radius=8,
        )

    # Add a special button with different styling
    button_list_2_cols.add_button(
        text="Special Button",
        command=lambda: button_action("Special Button"),
        fg_color="red",
        hover_color="darkred",
        text_color="yellow",
        font=customtkinter.CTkFont(size=16, weight="bold"),
        height=60,
    )

    # Add a button to clear all buttons in the first list
    def clear_all_buttons():
        button_list_2_cols.clear_buttons()
        print("All buttons cleared!")

    clear_button = customtkinter.CTkButton(
        master=app, text="Clear All Buttons (List 1)", command=clear_all_buttons
    )
    clear_button.grid(row=1, column=0, columnspan=2, pady=10)

    app.mainloop()

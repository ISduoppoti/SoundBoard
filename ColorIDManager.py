class ColorIDManager:
    def __init__(self):
        self.colors = [
            "#FF6B6B",  # Red
            "#4ECDC4",  # Teal
            "#45B7D1",  # Blue
            "#96CEB4",  # Green
            "#FFEAA7",  # Yellow
            "#DDA0DD",  # Plum
            "#98D8C8",  # Mint
            "#F7DC6F",  # Light Yellow
            "#BB8FCE",  # Light Purple
            "#85C1E9",  # Light Blue
            "#F8C471",  # Orange
            "#82E0AA",  # Light Green
        ]

        self.current_index = 0

    def set_id_color(self):
        """Returns the next color in the cycle and advances the index"""
        color = self.colors[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.colors)
        return color

    def reset_colors(self):
        """Reset color assignment to start from the beginning"""
        self.current_index = 0

    def get_current_color(self):
        """Get current color without advancing the index"""
        return self.colors[self.current_index]

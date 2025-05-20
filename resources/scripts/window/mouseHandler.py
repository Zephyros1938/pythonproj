class MouseHandler:
    def __init__(self):
        self.first_mouse = True
        self.last_x = 0.0
        self.last_y = 0.0
        self.x_offset = 0.0
        self.y_offset = 0.0

    def update(self, x: int, y: int):
        xpos = float(x)
        ypos = float(y)

        if self.first_mouse:
            self.last_x = xpos
            self.last_y = ypos
            self.first_mouse = False

        self.x_offset = xpos - self.last_x
        self.y_offset = self.last_y - ypos  # Reversed since y-coordinates go from bottom to top

        self.last_x = xpos
        self.last_y = ypos

    def get_offsets(self) -> tuple[float, float]:
        return self.x_offset, self.y_offset

    def reset_offsets(self):
        self.x_offset = 0.0
        self.y_offset = 0.0

    def set_first_mouse(self, fm: bool):
        self.first_mouse = fm

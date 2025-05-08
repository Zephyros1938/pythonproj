import glfw as GLFW

def default_window_hints() -> dict[int, int]:
    """
    Returns default GLFW window hints.

    Hints:
    - GLFW.CONTEXT_VERSION_MAJOR = 3
    - GLFW.CONTEXT_VERSION_MINOR = 3
    - GLFW.OPENGL_PROFILE = GLFW.OPENGL_CORE_PROFILE
    - GLFW.OPENGL_FORWARD_COMPAT = GLFW.TRUE
    - GLFW.VISIBLE = GLFW.FALSE
    """
    return {
        GLFW.CONTEXT_VERSION_MAJOR: 3,
        GLFW.CONTEXT_VERSION_MINOR: 3,
        GLFW.OPENGL_PROFILE: GLFW.OPENGL_CORE_PROFILE,
        GLFW.OPENGL_FORWARD_COMPAT: GLFW.TRUE,
        GLFW.VISIBLE: GLFW.FALSE,
    }


class Window:
    def __init__(self, viewport: tuple[int, int], name = "GLFW Window", hints: dict[int, int] = default_window_hints(), debug: bool = False):
        # makes sure that GLFW is initialized
        if not GLFW.init():
            raise Exception("[ERROR] Failed to intialize GLFW!")

        # set window hints
        for (hint, value) in hints.items():
            GLFW.window_hint(hint, value)

        # create window
        window = GLFW.create_window(viewport[0], viewport[1], name, None, None)

        # make sure that window was created
        if not window:
            GLFW.terminate()
            raise Exception("[ERROR] Failed to create GLFW Window!")

        # set GLFW's current window
        GLFW.make_context_current(window)
        self.handle = window

        if debug:
            from OpenGL.GL import glGetString, GL_VERSION
            print(f"[DEBUG] OpenGL Version: {glGetString(GL_VERSION)}")

    def destroy(self):
        """Kills the window"""
        GLFW.destroy_window(self.handle)
        GLFW.terminate()

    def poll_events(self):
        """Polls the window's events (keypresses, mouse movements, etc)"""
        GLFW.poll_events()

    def swap_buffers(self):
        """Swaps the windows buffers

            Should only be used AFTER the drawing is finished"""
        GLFW.swap_buffers(self.handle)

    def should_close(self) -> bool:
        """Returns whether or not the window has been told to close"""
        return GLFW.window_should_close(self.handle)

    def set_should_close(self, value: bool):
        """Sets whether or not the window should close"""
        GLFW.set_window_should_close(self.handle, value)

    def get_key(self, key):
        """Returns the specified key's state (pressed, held, etc)"""
        return GLFW.get_key(self.handle, key)

    def get_mouse_button(self, button):
        """Returns the specified mouse button's state (pressed, held, etc)"""
        return GLFW.get_mouse_button(self.handle, button)

    def get_cursor_pos(self):
        """Returns the mouse's current position"""
        return GLFW.get_cursor_pos(self.handle)

    def set_window_size(self, width, height):
        """Sets the windows size"""
        GLFW.set_window_size(self.handle, width, height)

    def get_window_size(self):
        """Returns the windows size"""
        return GLFW.get_window_size(self.handle)

    def show(self):
        """Shows the window"""
        GLFW.show_window(self.handle)

    def hide(self):
        """Hides the window"""
        GLFW.hide_window(self.handle)

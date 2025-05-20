import glfw as GLFW
import OpenGL.GL as GL

from resources.scripts import window
from resources.scripts.physics.time import Time
from resources.scripts.window import Window

class WindowHints:
    def __init__(self, name:str, flags: dict[int, int] = window.default_window_flags(), debugWindowCreation: bool = False, viewport: tuple[int, int] = (800, 600)):
        self.name = name
        self.flags = flags
        self.debugWindowCreation = debugWindowCreation
        self.viewport = viewport

def default_window_hints():
    return WindowHints("GLFW Window")

class GameWindow(Window):
    window: Window
    def __init__(self, hints: WindowHints = default_window_hints()):
        self._hints = hints
        self._time = Time(GLFW.get_time)

    def __update(self):
        gt = self._time.tick()
        self.update(gt.delta)

    def process_input(self):
        pass

    def update(self, deltatime: float):
        pass

    def run(self):
        self.on_init()
        self.show()
        while not self.should_close():
            self.poll_events()
            self.__update()
            self.render()
            self.swap_buffers()
        GLFW.terminate()

    def on_init(self):
        super().__init__(self._hints.viewport, self._hints.name, self._hints.flags, self._hints.debugWindowCreation)
        GLFW.set_window_user_pointer(self.handle, self)
        GLFW.set_key_callback(self.handle, self._key_callback)
        GLFW.set_cursor_pos_callback(self.handle, self._cursor_callback)
        GLFW.set_scroll_callback(self.handle, self._scroll_callback)
        GLFW.set_framebuffer_size_callback(self.handle, self._resize_callback)
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)

    def render(self):
        raise NotImplementedError()

    def _key_callback(self, window, key, scancode, action, mods):
        self = GLFW.get_window_user_pointer(window)
        if hasattr(self, "on_key"):
            self.on_key(key, scancode, action, mods)

    def _cursor_callback(self, window, xpos, ypos):
        self = GLFW.get_window_user_pointer(window)
        if hasattr(self, "on_mouse_move"):
            self.on_mouse_move(xpos, ypos)

    def _scroll_callback(self, window, xoffset, yoffset):
        self = GLFW.get_window_user_pointer(window)
        if hasattr(self, "on_scroll"):
            self.on_scroll(xoffset, yoffset)

    def _resize_callback(self, window, width, height):
        self = GLFW.get_window_user_pointer(window)
        if hasattr(self, "on_resize"):
            self.on_resize(width, height)

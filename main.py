import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import glfw as GLFW

def main():
    # makes sure that GLFW is initialized
    if not GLFW.init():
        raise Exception("Failed to intialize GLFW!")

    # set window hints
    GLFW.window_hint(GLFW.CONTEXT_VERSION_MAJOR, 3)
    GLFW.window_hint(GLFW.CONTEXT_VERSION_MINOR, 3)
    GLFW.window_hint(GLFW.OPENGL_PROFILE, GLFW.OPENGL_CORE_PROFILE)
    GLFW.window_hint(GLFW.OPENGL_FORWARD_COMPAT, GLFW.TRUE)
    GLFW.window_hint(GLFW.VISIBLE, GLFW.FALSE)

    # create window
    window = GLFW.create_window(800, 600, "GLFW Window", None, None)

    # make sure that window was created
    if not window:
        GLFW.terminate()
        raise Exception("Failed to create GLFW Window!")

    # set GLFW's current window
    GLFW.make_context_current(window)

    # set callbacks
    GLFW.set_key_callback(window, key_callback)

    # show the window
    GLFW.show_window(window)

    # main loop
    while not GLFW.window_should_close(window):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GLFW.swap_buffers(window)
        GLFW.poll_events()

    # terminates GLFW
    GLFW.terminate()

# key callback for pressing keys in window
def key_callback(window: GLFW._GLFWwindow, key: int, scancode: int, action: int, mods: int):
    if key == GLFW.KEY_ESCAPE:
        GLFW.set_window_should_close(window, GLFW.TRUE);
    else:
        if action == GLFW.RELEASE:
            print(chr(key))

if __name__ == "__main__":
    main()

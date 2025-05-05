import OpenGL.GL as GL
import OpenGL.GLUT as GLUT
import ctypes
import glfw


def main():
    # makes sure that GLFW is initialized
    if not glfw.init():
        raise Exception("Failed to intialize GLFW!")

    # set window hints
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    # create window
    window = glfw.create_window(800, 600, "GLFW Window", None, None)

    # make sure that window was created
    if not window:
        glfw.terminate()
        raise Exception("Failed to create GLFW Window!")

    # set glfw's current window
    glfw.make_context_current(window)
    
    

    # show the window
    glfw.show_window(window)

    # main loop
    while not glfw.window_should_close(window):
        glfw.swap_buffers(window)
        glfw.poll_events()

    # terminates GLFW
    glfw.terminate()


if __name__ == "__main__":
    main()

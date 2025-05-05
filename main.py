import OpenGL.GL as GL
# import OpenGL.GLUT as GLUT
import glfw as GLFW
import numpy as np
import ctypes
from ctypes import sizeof
from resources.scripts.shader import Shader

# null pointer
NULL_PTR = ctypes.c_void_p(0)

# triangle color points for drawing later
vertices = [
#   X     Y     Z    R    G    B
    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
     0.0,  0.5, 0.0, 0.0, 0.0, 1.0,
]

vertices = np.array(vertices, dtype=np.float32)

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

    # read at resources\scripts\shader.py 
    s = Shader("resources/shaders/test.vert", "resources/shaders/test.frag")

    # get 1 buffer name and 1 vertex array name
    VBO = GL.glGenBuffers(1)
    VAO = GL.glGenVertexArrays(1)

    # activate vertex arrays
    GL.glBindVertexArray(VAO)

    # Binds buffer to array, Initializes Buffer
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    GL.glBufferData(GL.GL_ARRAY_BUFFER, # Buffer to initialize
                    sizeof(ctypes.c_float) * len(vertices),  # Buffer size 
                    vertices, # Pointer for initialization
                    GL.GL_STATIC_DRAW # Used for drawing
                    )

    # Build the Array
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 6 * sizeof(ctypes.c_float), NULL_PTR)
    GL.glEnableVertexAttribArray(0)
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 6 * sizeof(ctypes.c_float), ctypes.c_void_p(3 * sizeof(ctypes.c_float)))
    GL.glEnableVertexAttribArray(1)
    
    # Deactivate everything
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    GL.glBindVertexArray(0)

    # Colors to use glClear with
    GL.glClearColor(0.0, 0.0, 0.0, 0.0)

    # show the window
    GLFW.show_window(window)

    # main loop
    while not GLFW.window_should_close(window):
        # Clear window?
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glUseProgram(s.ID)

        # Array drawing
        GL.glBindVertexArray(VAO)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
        GL.glBindVertexArray(0)

        # Draw window
        GLFW.swap_buffers(window)
        GLFW.poll_events()

    # terminates GLFW
    GLFW.terminate()

# key callback for pressing keys in window
def key_callback(window: GLFW._GLFWwindow, key: int, scancode: int, action: int, mods: int):
    # if ESC is pressed, close window
    if key == GLFW.KEY_ESCAPE:
        GLFW.set_window_should_close(window, GLFW.TRUE);
    else:
        if action == GLFW.RELEASE:
            print(chr(key))

if __name__ == "__main__":
    main()

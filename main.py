import OpenGL.GL as GL
import glfw as GLFW
import numpy as np
import ctypes
from ctypes import sizeof

from pyglm.glm import translate, rotate, scale
from resources.scripts.shader import Shader
from resources.scripts.camera.camera3d import Camera3D
from glm import ivec2, mat4, vec3, radians

NULL_PTR = ctypes.c_void_p(0)
VIEWPORT = ivec2(800, 600)
SHADERS: dict[str, Shader] = {}
DELTATIME: float  = 0.0
LASTFRAME: float  = 0.0
FIRSTMOUSE: bool  = False
LAST_X : float = 0
LAST_Y : float = 0

model = mat4(1.0)
model = translate(model, vec3(0.0, 0.0, -5.0))
model = rotate(model, radians(45.0), vec3(0.0, 1.0, 0.0))
model = scale(model, vec3(1.0))


CAMERA = Camera3D()

vertices = [
#   X     Y     Z    R    G    B
    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
     0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
     0.0,  0.5, 0.0, 0.0, 0.0, 1.0
]

s = None

def main():
    global FIRSTMOUSE
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
    window = GLFW.create_window(VIEWPORT.x, VIEWPORT.y, "GLFW Window", None, None)

    # make sure that window was created
    if not window:
        GLFW.terminate()
        raise Exception("Failed to create GLFW Window!")

    # set GLFW's current window
    GLFW.make_context_current(window)
    GL.glEnable(GL.GL_DEPTH_TEST)

    # set callbacks
    GLFW.set_key_callback(window, key_callback)
    GLFW.set_framebuffer_size_callback(window, framebuffer_resize_callback)
    GLFW.set_cursor_pos_callback(window, cursor_pos_callback)
    GLFW.set_scroll_callback(window, scroll_callback)

    SHADERS["main"] = Shader("resources/shaders/test.vert", "resources/shaders/test.frag")

    # vertex buffer object
    #   stores vertex data and is tied to the VAO
    VBO = GL.glGenBuffers(1)
    # vertex array object
    #   holds vbos
    VAO = GL.glGenVertexArrays(1)

    # tell the gpu that this is the VAO being used
    GL.glBindVertexArray(VAO)

    # bind the VBO
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, VBO)
    # add the data (vertices)
    # GL_ARRAY_BUFFER
    #   tell gpu this is an array of vertices
    # sizeof * len
    #   tell gpu the size of the buffer
    # vertices
    #   send vertices to gpu
    # GL_STATIC_DRAW
    #   statically draw the buffer, do not expect changes
    GL.glBufferData(GL.GL_ARRAY_BUFFER, sizeof(ctypes.c_float) * len(vertices), np.array(vertices, dtype=np.float32), GL.GL_STATIC_DRAW)

    # first 3 elements are position, total size is 6 as it stores (position, color)
    GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, 6 * sizeof(ctypes.c_float), NULL_PTR)
    GL.glEnableVertexAttribArray(0)
    # colors
    GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, 6 * sizeof(ctypes.c_float), ctypes.c_void_p(3 * sizeof(ctypes.c_float)))
    GL.glEnableVertexAttribArray(1)

    # unbind the VBO
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    # unbind the VAO
    GL.glBindVertexArray(0)

    # tell gpu that the background color is black
    GL.glClearColor(0.0, 0.0, 0.0, 0.0)
    GL.glViewport(0, 0, VIEWPORT.x, VIEWPORT.y);

    SHADERS["main"].activate()
    SHADERS["main"].setMat4fv("model", model)
    SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())
    SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())


    # show the window
    GLFW.show_window(window)

    # capture the cursor
    GLFW.set_input_mode(window, GLFW.CURSOR, GLFW.CURSOR_DISABLED)
    FIRSTMOUSE = True

    # main loop
    while not GLFW.window_should_close(window):
        update_deltatime()
        process_input(window)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        SHADERS["main"].activate()
        SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())
        SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())

        GL.glBindVertexArray(VAO)
        GL.glDrawArrays(SHADERS["main"].DRAWMODE, 0, 3)
        GL.glBindVertexArray(0)

        GLFW.swap_buffers(window)
        GLFW.poll_events()

    # terminates GLFW
    GLFW.terminate()

# for non-continuous input
def key_callback(window: GLFW._GLFWwindow, k: int, sc: int, a: int, mod: int):
    if k == GLFW.KEY_ESCAPE and a == GLFW.PRESS:
        GLFW.set_window_should_close(window, GLFW.TRUE)
    elif a == GLFW.PRESS:
        if   k == GLFW.KEY_1: SHADERS["main"].DRAWMODE = GL.GL_TRIANGLES
        elif k == GLFW.KEY_2: SHADERS["main"].DRAWMODE = GL.GL_LINES
        elif k == GLFW.KEY_3: SHADERS["main"].DRAWMODE = GL.GL_LINE_STRIP
        elif k == GLFW.KEY_4: SHADERS["main"].DRAWMODE = GL.GL_LINE_LOOP
        elif k == GLFW.KEY_5: SHADERS["main"].DRAWMODE = GL.GL_POINTS
        if k == GLFW.KEY_MINUS:
            GLFW.set_input_mode(window, GLFW.CURSOR, GLFW.CURSOR_NORMAL)
            global FIRSTMOUSE
            FIRSTMOUSE = True
        if k == GLFW.KEY_EQUAL:
            GLFW.set_input_mode(window, GLFW.CURSOR, GLFW.CURSOR_DISABLED)

# for continuous input, such as movement
#   called per-frame
def process_input(window: GLFW._GLFWwindow):
    if GLFW.get_key(window, GLFW.KEY_W) == GLFW.PRESS:
        CAMERA.process_keyboard(0, DELTATIME)
    if GLFW.get_key(window, GLFW.KEY_S) == GLFW.PRESS:
        CAMERA.process_keyboard(1, DELTATIME)
    if GLFW.get_key(window, GLFW.KEY_A) == GLFW.PRESS:
        CAMERA.process_keyboard(2, DELTATIME)
    if GLFW.get_key(window, GLFW.KEY_D) == GLFW.PRESS:
        CAMERA.process_keyboard(3, DELTATIME)
    if not GLFW.get_key(window, GLFW.KEY_LEFT_SHIFT) == GLFW.PRESS:
        if GLFW.get_key(window, GLFW.KEY_LEFT_CONTROL) == GLFW.PRESS:
            CAMERA.process_keyboard(4, DELTATIME)
        if GLFW.get_key(window, GLFW.KEY_SPACE) == GLFW.PRESS:
            CAMERA.process_keyboard(5, DELTATIME)
    else:
        if GLFW.get_key(window, GLFW.KEY_LEFT_CONTROL) == GLFW.PRESS:
            CAMERA.process_keyboard(6, DELTATIME)
        if GLFW.get_key(window, GLFW.KEY_SPACE) == GLFW.PRESS:
            CAMERA.process_keyboard(7, DELTATIME)


def cursor_pos_callback(window: GLFW._GLFWwindow, x:int, y:int):
    if GLFW.get_input_mode(window, GLFW.CURSOR) == GLFW.CURSOR_DISABLED:
        global LAST_X, LAST_Y, FIRSTMOUSE
        xpos = float(x)
        ypos = float(y)
        if FIRSTMOUSE:
            LAST_X = xpos
            LAST_Y = ypos
            FIRSTMOUSE = False

        xoffset = xpos - LAST_X
        yoffset = LAST_Y - ypos


        LAST_X = xpos
        LAST_Y = ypos

        CAMERA.process_mouse(xoffset, yoffset)

def scroll_callback(window: GLFW._GLFWwindow, _, yoffset: float):
    CAMERA.process_scroll(yoffset)


def framebuffer_resize_callback(window: GLFW._GLFWwindow, width: int, height: int):
    VIEWPORT = ivec2(width, height)
    GL.glViewport(0, 0, VIEWPORT.x, VIEWPORT.y)
    CAMERA.set_aspect_ratio(VIEWPORT.x / VIEWPORT.y)

def update_deltatime():
    global LASTFRAME, DELTATIME
    currentframe: float = GLFW.get_time()
    DELTATIME = currentframe - LASTFRAME
    LASTFRAME = currentframe

if __name__ == "__main__":
    main()

import lib
from lib import cstr
lib.init()
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "INFO"))

import OpenGL.GL as GL
import glfw as GLFW
import threading

from pyglm.glm import translate, rotate, scale, ivec2, mat4, vec3, length, sin,cos
from resources.scripts.shader import Shader, ShaderBuilder
from resources.scripts.verticeMesh import VerticeMesh
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.camera.camera3d import Camera3D
from resources.scripts.glfwUtilities import getKeyPressed
from resources.scripts.window import Window
from resources.scripts.texture import Texture


VIEWPORT = ivec2(800, 600)
SHADERS: dict[str, Shader] = {}
DELTATIME: float  = 0.0
LASTFRAME: float  = 0.0
FIRSTMOUSE: bool  = True
LAST_X : float = 0
LAST_Y : float = 0

model = mat4(1.0)
model = translate(model, vec3(0.0, 0.0, 0.0))
model = scale(model, vec3(5.0))

CAMERA = Camera3D(move_speed=20, far=1000)

# triangle color points for drawing later
# XYZ, RGB

vertices = VerticeMesh([
    0.0, 0.5, 0.0,
    -0.5, 0.0, 0.5,
    0.5, 0.0, 0.5,

    0.0, 0.5, 0.0,
    -0.5, 0.0, -0.5,
    -0.5, 0.0, 0.5,

    0.0, 0.5, 0.0,
    0.5, 0.0, 0.5,
    0.5, 0.0, -0.5,

    0.0, 0.5, 0.0,
    0.5, 0.0, -0.5,
    -0.5, 0.0, -0.5,

    0.0, -0.5, 0.0,
    0.5, 0.0, 0.5,
    -0.5, 0.0, 0.5,

    0.0, -0.5, 0.0,
    -0.5, 0.0, 0.5,
    -0.5, 0.0, -0.5,

    0.0, -0.5, 0.0,
    0.5, 0.0, -0.5,
    0.5, 0.0, 0.5,

    0.0, -0.5, 0.0,
    -0.5, 0.0, -0.5,
    0.5, 0.0, -0.5,

])
colors = VerticeMesh([0.0 if i % 9 in [1, 2, 3, 5, 6, 7] else 1.0 for i in range(len(vertices.vertices))])

verticeModel = VerticeModel({"vertices": vertices, "colors": colors})

def main():
    global FIRSTMOUSE, model

    window = Window( viewport=(VIEWPORT.x, VIEWPORT.y))

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)

    # set callbacks
    GLFW.set_key_callback(window.handle, key_callback)
    GLFW.set_framebuffer_size_callback(window.handle, framebuffer_resize_callback)
    GLFW.set_cursor_pos_callback(window.handle, cursor_pos_callback)
    GLFW.set_scroll_callback(window.handle, scroll_callback)

    SHADERS["main"], svao = ShaderBuilder("resources/shaders/test.vert", "resources/shaders/test.frag", 3).fromVerticeModel(verticeModel, [(0, 3), (1, 3)])

    GL.glClearColor(0.0, 0.0, 0.0, 0.0)

    SHADERS["main"].activate()
    SHADERS["main"].setMat4fv("model", model)
    SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())
    SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())

    # capture the cursor
    GLFW.set_input_mode(window.handle, GLFW.CURSOR, GLFW.CURSOR_DISABLED)

    t0 = 25
    t1 = 25
    t2 = 25
    t = [vec3(x, y, z) for x in range(-t0, t0+1) for y in range(-t1, t1+1) for z in range(-t2, t2+1)]

    # show the window
    window.show()
    GL.glViewport(0, 0, VIEWPORT.x, VIEWPORT.y)

    tt: Texture = Texture("resources/textures/egg.png", "")

    def fps_notify():
        from time import sleep
        global DELTATIME
        averageFps = 0
        updateRate = 1.0
        while True:
            if not DELTATIME <= 0:
                fps = updateRate / DELTATIME
                averageFps += fps
                averageFps /= 2
                # logger.info(1, cstr(f"FPS: {fps:.2f}\tAVERAGE: {averageFps:.2f}"))
            sleep(updateRate)

    # Start the thread
    fps_notify_thread = threading.Thread(target=fps_notify, daemon=True)
    fps_notify_thread.start()

    # main loop
    while not window.should_close():
        update_deltatime()
        process_input(window.handle)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT) # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # clear the color buffer

        SHADERS["main"].activate()
        SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())
        SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())

        movepos = vec3(cos(GLFW.get_time()) * 7.5, 0.0, sin(GLFW.get_time()) * 7.5)
        cullsize = 5.0
        filtered = [n for n in t if length(movepos - n) <= cullsize]
        for n in [translate(model, n) for n in filtered]:
            # print(f"[Render] Drawing model matrix: {n}")
            SHADERS["main"].activate()
            SHADERS["main"].setMat4fv("model", n)
            verticeModel.draw(SHADERS["main"], svao)

        # Draw window
        window.swap_buffers()
        window.poll_events()

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
    if getKeyPressed(window, GLFW.KEY_W):
        CAMERA.process_keyboard(0, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_S):
        CAMERA.process_keyboard(1, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_A):
        CAMERA.process_keyboard(2, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_D):
        CAMERA.process_keyboard(3, DELTATIME)
    if not getKeyPressed(window, GLFW.KEY_LEFT_SHIFT):
        if getKeyPressed(window, GLFW.KEY_LEFT_CONTROL):
            CAMERA.process_keyboard(4, DELTATIME)
        if getKeyPressed(window, GLFW.KEY_SPACE):
            CAMERA.process_keyboard(5, DELTATIME)
    else:
        if getKeyPressed(window, GLFW.KEY_LEFT_CONTROL):
            CAMERA.process_keyboard(6, DELTATIME)
        if getKeyPressed(window, GLFW.KEY_SPACE):
            CAMERA.process_keyboard(7, DELTATIME)
    global model
    if getKeyPressed(window, GLFW.KEY_UP):
        model = rotate(model, -DELTATIME, vec3(1,0,0))
    if getKeyPressed(window, GLFW.KEY_DOWN):
        model = rotate(model, DELTATIME, vec3(1,0,0))
    if getKeyPressed(window, GLFW.KEY_LEFT):
        model = rotate(model, -DELTATIME, vec3(0,1,0))
    if getKeyPressed(window, GLFW.KEY_RIGHT):
        model = rotate(model, DELTATIME, vec3(0,1,0))


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
    GL.glViewport(0, 0, width, height)
    CAMERA.set_aspect_ratio(width / height)

def update_deltatime():
    global LASTFRAME, DELTATIME
    currentframe: float = GLFW.get_time()
    DELTATIME = currentframe - LASTFRAME
    LASTFRAME = currentframe

if __name__ == "__main__":
    main()

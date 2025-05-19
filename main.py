import lib
from lib import cstr
lib.init(debug=True, debugLibInternals=True)
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "INFO"))
assimp = lib.getlib("assimp")
print(assimp.aiGetErrorString())
print(lib.getEnum("assimp", "aiPostProcessSteps").aiProcess_CalcTangentSpace.value)

import OpenGL.GL as GL
import glfw as GLFW
import threading

from pyglm.glm import translate, rotate, scale, ivec2, mat4, vec2, vec3, vec4, length, sin,cos, radians, pi as PI, exp, distance
from resources.scripts.shader import Shader, ShaderBuilder
from resources.scripts.verticeMesh import VerticeMesh
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.camera.camera3d import Camera3D
from resources.scripts.glfwUtilities import getKeyPressed
from resources.scripts.window import Window
from resources.scripts.object import Obj, VerticeModelObject, Skybox

VIEWPORT = ivec2(800, 600)
SHADERS: dict[str, Shader] = {}
DELTATIME: float  = 0.0
LASTFRAME: float  = 0.0
FIRSTMOUSE: bool  = True
LAST_X : float = 0
LAST_Y : float = 0

CAMERA = Camera3D(move_speed=20, far=1000)

vertices = VerticeMesh([
    -10,-2, 0,
     10,-2, 0,
     10, 0, 0,
     -10,-2, 0,
     10, 0, 0,
     -10, 0, 0,

])
colors = VerticeMesh([
    1,0,0,
    0,1,0,
    0,0,1,
    1,0,0,
    0,1,0,
    0,0,1
])

verticeModel = VerticeModel({"vertices": vertices, "colors": colors})






o = VerticeModelObject(verticeModel, vec3(0,0,-3), vec3(0))

objects: list[Obj] = []

def main():
    global FIRSTMOUSE, model

    window = Window( viewport=(VIEWPORT.x, VIEWPORT.y))

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);

    # set callbacks
    GLFW.set_key_callback(window.handle, key_callback)
    GLFW.set_framebuffer_size_callback(window.handle, framebuffer_resize_callback)
    # GLFW.set_cursor_pos_callback(window.handle, cursor_pos_callback)
    GLFW.set_scroll_callback(window.handle, scroll_callback)

    SHADERS["main"], svao = ShaderBuilder("resources/shaders/test.vert", "resources/shaders/test.frag", 3).fromVerticeModel(verticeModel, [(0, 3), (1, 3)])
    sb = Skybox(vec3(0), vec3(0), "resources/textures/skyboxes/grassy1.png")
    objects.append(sb)
    objects.append(o)

    GL.glClearColor(0.0, 0.0, 0.0, 0.0)

    SHADERS["main"].activate()
    SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())
    SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())

    # capture the cursor
    GLFW.set_input_mode(window.handle, GLFW.CURSOR, GLFW.CURSOR_DISABLED)

    # show the window
    window.show()
    GL.glViewport(0, 0, VIEWPORT.x, VIEWPORT.y)

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
                logger.info(1, cstr(f"FPS: {fps:.2f}\tAVERAGE: {averageFps:.2f}"))
            sleep(updateRate)

    # Start the thread
    fps_notify_thread = threading.Thread(target=fps_notify, daemon=True)
    fps_notify_thread.start()

    # main loop
    while not window.should_close():
        update_deltatime()
        process_input(window.handle)
        sb.pos = CAMERA.position
        for x in objects:
            x.update(DELTATIME)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT) # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # clear the color buffer

        SHADERS["main"].activate()
        SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())
        SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())


        # o.draw(SHADERS["main"], svao)
        for x in objects:
            if isinstance(x, VerticeModelObject):
                x.draw(SHADERS["main"], svao)
            elif isinstance(x, Skybox):
                x.shader.activate()
                x.shader.setMat4fv("projection", CAMERA.getProjectionMatrix())
                x.shader.setMat4fv("view", CAMERA.getViewMatrix())
                x.draw()

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
    # if getKeyPressed(window, GLFW.KEY_UP):
    #     CAMERA.process_keyboard(0, DELTATIME)
    # if getKeyPressed(window, GLFW.KEY_DOWN):
    #     CAMERA.process_keyboard(1, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_LEFT):
        CAMERA.process_keyboard(2, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_RIGHT):
        CAMERA.process_keyboard(3, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_SPACE):
        CAMERA.process_keyboard(7, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_LEFT_CONTROL):
        CAMERA.process_keyboard(6, DELTATIME)



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

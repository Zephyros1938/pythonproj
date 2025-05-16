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

from pyglm.glm import translate, rotate, scale, ivec2, mat4, vec3, length, sin,cos, radians, pi as PI
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

CAMERA = Camera3D(move_speed=20, far=1000)

# triangle color points for drawing later
# XYZ, RGB

vertices = VerticeMesh([
    -2, -2, 0,
    2, -2, 0,
    2, 2, 0,

    -2, -2, 0,
    2, 2, 0,
    -2, 2, 0
])
colors = VerticeMesh([0.0 if i % 9 in [1, 2, 3, 5, 6, 7] else 1.0 for i in range(len(vertices.vertices))])

verticeModel = VerticeModel({"vertices": vertices, "colors": colors})

class Obj:
    vm: VerticeModel
    pos: vec3
    rot: vec3
    posVel: vec3
    rotVel: vec3
    model: mat4
    def __init__(self, vm, pos, rot):
        self.vm = vm
        self.pos = pos
        self.rot = rot
        self.posVel = vec3(0)
        self.rotVel = vec3(0)
        self.model = mat4(1.0)

    def update(self, dt: float):
        damping = 1.0 - (dt * 5.0)
        self.model[3][0] += self.posVel.x * dt
        self.model[3][1] += self.posVel.y * dt
        self.model[3][2] += self.posVel.z * dt
        self.rot += self.rotVel * dt
        self.posVel *= damping
        self.rotVel *= damping

    def draw(self, shader:Shader, vao: int):
        shader.activate()
        shader.setMat4fv("model", translate(self.model, self.pos))
        self.vm.draw(shader, vao)

    def __rotate(self):
        rx = radians(self.rot.x)
        ry = radians(self.rot.y)
        rz = radians(self.rot.z)
        #x
        self.model[1][1] *= cos(rx)
        self.model[1][2] *= -sin(rx)
        self.model[2][1] *= sin(rx)
        self.model[2][2] *= cos(rx)

o = Obj(verticeModel, vec3(0), vec3(0))


def main():
    print(rotate(mat4(1), radians(90), vec3(1,0,0)))
    print(rotate(mat4(1), radians(90), vec3(0,1,0)))
    print(rotate(mat4(1), radians(90), vec3(0,0,1)))
    global FIRSTMOUSE, model

    window = Window( viewport=(VIEWPORT.x, VIEWPORT.y))

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glEnable(GL.GL_CULL_FACE)

    # set callbacks
    GLFW.set_key_callback(window.handle, key_callback)
    GLFW.set_framebuffer_size_callback(window.handle, framebuffer_resize_callback)
    # GLFW.set_cursor_pos_callback(window.handle, cursor_pos_callback)
    GLFW.set_scroll_callback(window.handle, scroll_callback)

    SHADERS["main"], svao = ShaderBuilder("resources/shaders/test.vert", "resources/shaders/test.frag", 3).fromVerticeModel(verticeModel, [(0, 3), (1, 3)])

    GL.glClearColor(0.0, 0.0, 0.0, 0.0)

    SHADERS["main"].activate()
    SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())
    SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())

    # capture the cursor
    GLFW.set_input_mode(window.handle, GLFW.CURSOR, GLFW.CURSOR_DISABLED)

    # show the window
    window.show()
    GL.glViewport(0, 0, VIEWPORT.x, VIEWPORT.y)

    tt: Texture = Texture("resources/textures/help.png", "")

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
        o.update(DELTATIME)
        process_input(window.handle)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT) # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # clear the color buffer



        SHADERS["main"].activate()
        SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())
        SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())

        o.draw(SHADERS["main"], svao)

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
    if getKeyPressed(window, GLFW.KEY_UP):
        CAMERA.process_keyboard(0, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_DOWN):
        CAMERA.process_keyboard(1, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_LEFT):
        CAMERA.process_keyboard(2, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_RIGHT):
        CAMERA.process_keyboard(3, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_A):
        o.posVel.x -= 25 * DELTATIME
    if getKeyPressed(window, GLFW.KEY_D):
        o.posVel.x += 25 * DELTATIME
    if getKeyPressed(window, GLFW.KEY_W):
        o.posVel.y += 25 * DELTATIME
    if getKeyPressed(window, GLFW.KEY_S):
        o.posVel.y -= 25 * DELTATIME


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

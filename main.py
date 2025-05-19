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
import numpy as np
from numpy import array as nparray, float32, uint32
from ctypes import c_void_p
import ctypes

from pyglm.glm import translate, rotate, scale, ivec2, mat4, vec2, vec3, vec4, length, sin,cos, radians, pi as PI, exp, distance
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



class Obj:
    vm: 'VerticeModel'
    pos: vec3
    rot: vec3
    posVel: vec3
    rotVel: vec3
    model: mat4

    def __init__(self, vm: VerticeModel, pos: vec3, rot: vec3):
        self.vm = vm
        self.pos = pos
        self.rot = rot
        self.posVel = vec3(0.0)
        self.rotVel = vec3(0.0)
        self.model = mat4(1.0)

    def update(self, dt: float):
        drag = 1  # drag coefficient (adjust as needed)

        # Update position and rotation from velocity
        self.pos += self.posVel * dt
        self.rot += self.rotVel * dt

        # Apply exponential damping
        self.posVel *= exp(-drag * dt)
        self.rotVel *= exp(-drag * dt)

        # Threshold to prevent float drift
        if length(self.posVel) < 1e-4:
            self.posVel = vec3(0.0)
        if length(self.rotVel) < 1e-4:
            self.rotVel = vec3(0.0)

        # Update model matrix
        self.__update_model()

    def __update_model(self):
        self.model = mat4(1.0)
        self.model = translate(self.model, self.pos)
        self.__rotate()

    def __rotate(self):
        rx = radians(self.rot.x)
        ry = radians(self.rot.y)
        rz = radians(self.rot.z)

        # Apply rotation around X, Y, Z in order
        self.model = rotate(self.model, rx, vec3(1.0, 0.0, 0.0))
        self.model = rotate(self.model, ry, vec3(0.0, 1.0, 0.0))
        self.model = rotate(self.model, rz, vec3(0.0, 0.0, 1.0))

    def draw(self, shader: Shader, vao: int):
        shader.activate()
        shader.setMat4fv("model", self.model)
        self.vm.draw(shader, vao)

class Skybox:
    vertices: list[float] = [
        -1,-1,-1, 1,-1,-1, 1, 1,-1, #012
        -1,-1,-1, 1, 1,-1,-1, 1,-1, #023
        -1,-1, 1, 1, 1, 1, 1,-1, 1,
        -1,-1, 1,-1, 1, 1, 1, 1, 1,


        -1,-1,-1, 1,-1, 1, 1,-1,-1,
        -1,-1,-1,-1,-1, 1, 1,-1, 1,
        -1, 1,-1, 1, 1,-1, 1, 1, 1,
        -1, 1,-1, 1, 1, 1,-1, 1, 1,


        -1,-1,-1,-1, 1,-1,-1, 1, 1,
        -1,-1,-1,-1, 1, 1,-1,-1, 1,
         1,-1,-1, 1, 1, 1, 1, 1,-1,
         1,-1,-1, 1,-1, 1, 1, 1, 1,
    ]
    showing: bool = True
    shader: Shader
    image: Texture
    vao: int
    pos: vec3
    rot: vec3
    posVel: vec3
    rotVel: vec3
    model: mat4
    def __init__(self, rot:vec3, pos:vec3, imagePath: str):
        self.rot = rot
        self.pos = pos
        self.posVel = vec3(0)
        self.rotVel = vec3(0)
        self.model = scale(mat4(1),vec3(100))
        self.image = Texture(imagePath, "")

        texcoords = [
            # front
            0.25,1/3 ,0.5 ,1/3 ,0.5 ,2/3 , #012
            0.25,1/3 ,0.5 ,2/3 ,0.25,2/3 , #023

            # bottom
            1.00,1/3 ,0.75,2/3 ,0.75,1/3 , #023
            1.00,1/3 ,1.00,2/3 ,0.75,2/3 , #012

            # top
            0.25,1/3 ,0.50,000 ,0.50,1/3 , #012
            0.25,1/3 ,0.25,000 ,0.50,000 , #023

            # bottom
            0.25,2/3 ,0.50,2/3 ,0.50,1   , #023
            0.25,2/3 ,0.50,1   ,0.25,1   , #012

            # left
            0.25,1/3 ,0.25,2/3 ,0.00,2/3 , #012
            0.25,1/3 ,0.00,2/3 ,0.00,1/3 , #023

            # right
            0.50,1/3 ,0.75,2/3 ,0.50,2/3 , #023
            0.50,1/3 ,0.75,1/3 ,0.75,2/3 , #012
        ]

        varray = nparray(self.vertices, dtype=float32)
        tcarray = nparray(texcoords, dtype=float32)

        self.shader = Shader("resources/shaders/skybox.vert", "resources/shaders/skybox.frag")
        vao = GL.glGenVertexArrays(1)
        vbo = GL.glGenBuffers(1)
        tbo = GL.glGenBuffers(1)
        GL.glBindVertexArray(vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, varray.nbytes, varray, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(0,3,GL.GL_FLOAT,GL.GL_FALSE,3 * ctypes.sizeof(ctypes.c_float),c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, tbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, tcarray.nbytes, tcarray, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(1,2,GL.GL_FLOAT,GL.GL_FALSE,2 * ctypes.sizeof(ctypes.c_float),c_void_p(0 * ctypes.sizeof(ctypes.c_float)))
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        self.vao = vao
    def draw(self):
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.image.id)
        self.shader.activate()
        self.shader.setMat4fv("model", self.model)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
        GL.glUseProgram(0)
    def update(self, dt: float):
        drag = 1  # drag coefficient (adjust as needed)

        # Update position and rotation from velocity
        self.pos += self.posVel * dt
        self.rot += self.rotVel * dt

        # Apply exponential damping
        self.posVel *= exp(-drag * dt)
        self.rotVel *= exp(-drag * dt)

        # Threshold to prevent float drift
        if length(self.posVel) < 1e-4:
            self.posVel = vec3(0.0)
        if length(self.rotVel) < 1e-4:
            self.rotVel = vec3(0.0)

        # Update model matrix
        self.__update_model()

    def __update_model(self):
        self.model = mat4(1.0)
        self.model = translate(self.model, self.pos)
        self.__rotate()

    def __rotate(self):
        rx = radians(self.rot.x)
        ry = radians(self.rot.y)
        rz = radians(self.rot.z)

        # Apply rotation around X, Y, Z in order
        self.model = rotate(self.model, rx, vec3(1.0, 0.0, 0.0))
        self.model = rotate(self.model, ry, vec3(0.0, 1.0, 0.0))
        self.model = rotate(self.model, rz, vec3(0.0, 0.0, 1.0))


o = Obj(verticeModel, vec3(0), vec3(0))

Objs = []

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

    SHADERS["main"], svao = ShaderBuilder("resources/shaders/test.vert", "resources/shaders/test.frag", 3).fromVerticeModel(verticeModel, [(0, 3), (1, 3)], [np.float32, np.float32])
    sb = Skybox(vec3(0), vec3(0), "resources/textures/skyboxes/grassy1.png")

    GL.glClearColor(1.0, 1.0, 1.0, 0.0)

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
        o.update(DELTATIME)
        p = o
        for x in Objs:
            x.update(DELTATIME)
            dir: vec2 = (x.pos.xy - p.pos.xy);
            dist = distance(p.pos.xy, x.pos.xy);
            # if dist < .1:
            #     x.pos.xy = vec2(random.uniform(p.pos.x - 100,p.pos.x + 100),random.uniform(p.pos.y-100,p.pos.y+100))
            x.posVel.xy -= dir * dist * DELTATIME;
            p = x
        # CAMERA.position.xy = o.pos.xy
        process_input(window.handle)
        sb.pos = CAMERA.position
        sb.rotVel.y = 20
        sb.update(DELTATIME)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT) # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # clear the color buffer

        sb.shader.activate()
        sb.shader.setMat4fv("projection", CAMERA.getProjectionMatrix())
        sb.shader.setMat4fv("view", CAMERA.getViewMatrix())
        sb.draw()



        SHADERS["main"].activate()
        SHADERS["main"].setMat4fv("view", CAMERA.getViewMatrix())
        SHADERS["main"].setMat4fv("projection", CAMERA.getProjectionMatrix())


        # o.draw(SHADERS["main"], svao)
        for x in Objs:
            x.draw(SHADERS["main"], svao)

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
    if getKeyPressed(window, GLFW.KEY_SPACE):
        CAMERA.process_keyboard(7, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_LEFT_CONTROL):
        CAMERA.process_keyboard(6, DELTATIME)
    if getKeyPressed(window, GLFW.KEY_A):
        o.posVel.x -= 50 * DELTATIME
        o.rotVel.y += 180 * DELTATIME

    if getKeyPressed(window, GLFW.KEY_D):
        o.posVel.x += 50 * DELTATIME
        o.rotVel.y -= 180 * DELTATIME

    if getKeyPressed(window, GLFW.KEY_W):
        o.posVel.y += 50 * DELTATIME
        o.rotVel.x -= 180 * DELTATIME

    if getKeyPressed(window, GLFW.KEY_S):
        o.posVel.y -= 50 * DELTATIME
        o.rotVel.x += 180 * DELTATIME
    if getKeyPressed(window, GLFW.KEY_E):
        Objs.append(Obj(verticeModel, vec3(0,0,-1*len(Objs)), vec3(0)))



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

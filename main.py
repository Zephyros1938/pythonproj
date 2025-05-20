import lib
lib.init(debug=True, debugLibInternals=True)
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "INFO"))

import OpenGL.GL as GL
import glfw as GLFW

from pyglm.glm import vec3
from resources.scripts.shader import Shader, ShaderBuilder
from resources.scripts.verticeMesh import VerticeMesh
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.camera.camera3d import Camera3D
from resources.scripts.glfwUtilities import getKeyPressed
from resources.scripts.object import Obj, VerticeModelObject, Skybox
from resources.scripts.window.mouseHandler import MouseHandler
from resources.scripts.gameWindow import GameWindow

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

class CoolWindow(GameWindow):
    skybox   : Skybox
    objects  : list[Obj]
    shaders  : list[Shader]
    def __init__(self):
        super().__init__()
        self.objects  : list[Obj]    = []
        self.shaders  : list[Shader] = []

    def update(self, deltatime: float):
        self.skybox.update(deltatime)
        self.skybox.rotVel.y=20
        self.skybox.rotVel.x=15
        self.skybox.rotVel.z=10
        for o in self.objects:
            o.update(deltatime)

        # camera movement

        if getKeyPressed(self.handle, GLFW.KEY_W):
            self.camera.process_keyboard(0, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_S):
            self.camera.process_keyboard(1, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_A):
            self.camera.process_keyboard(2, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_D):
            self.camera.process_keyboard(3, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_SPACE):
            self.camera.process_keyboard(7, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_LEFT_CONTROL):
            self.camera.process_keyboard(6, deltatime)

    def on_init(self):
        super().on_init()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);
        self.skybox = Skybox(vec3(0), vec3(0), "resources/textures/skyboxes/grassy1.png")
        self.objects.append(
            VerticeModelObject(
                verticeModel,
                vec3(0,0,-3),
                vec3(0),
                (
                    ShaderBuilder(
                        "resources/shaders/test.vert",
                        "resources/shaders/test.frag",
                        3),
                    [
                        (0, 3),
                        (1, 3)
                    ]
                )
            )
        )
        self.mouseHandler = MouseHandler()
        self.camera = Camera3D(move_speed=20, far=1000)

    def render(self):
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT) # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # clear the color buffer
        self.skybox.shader.activate()
        self.skybox.shader.setMat4fv("projection", self.camera.getProjectionMatrix())
        self.skybox.shader.setMat4fv("view", self.camera.getViewMatrix())
        self.skybox.draw()
        for x in self.objects:
            x.shader.activate()
            x.shader.setMat4fv("projection", self.camera.getProjectionMatrix())
            x.shader.setMat4fv("view", self.camera.getViewMatrix())
            x.draw()

    def on_key(self, key, scancode, action, mods):
        if key == GLFW.KEY_ESCAPE and action == GLFW.PRESS:
            self.set_should_close(True)
        elif action == GLFW.PRESS:
            if key == GLFW.KEY_MINUS:
                GLFW.set_input_mode(self.handle, GLFW.CURSOR, GLFW.CURSOR_NORMAL)
                self.mouseHandler.set_first_mouse(True)
            if key == GLFW.KEY_EQUAL:
                GLFW.set_input_mode(self.handle, GLFW.CURSOR, GLFW.CURSOR_DISABLED)

    def on_resize(self, width, height):
        GL.glViewport(0, 0, width, height)
        self.camera.set_aspect_ratio(width / height)

    def on_mouse_move(self, xoffset, yoffset):
        if GLFW.get_input_mode(self.handle, GLFW.CURSOR) == GLFW.CURSOR_DISABLED:
            self.mouseHandler.update(xoffset, yoffset)
            self.camera.process_mouse(self.mouseHandler.x_offset, self.mouseHandler.y_offset)

    def on_scroll(self, xoffset, yoffset):
        self.camera.process_scroll(yoffset)

if __name__ == "__main__":
    cw = CoolWindow()
    cw.run()

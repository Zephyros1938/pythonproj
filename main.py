import lib
from resources.scripts.physics.transform import Transform, getTransformAABBCollision
lib.init(debug=False, debugLibInternals=False)
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "INFO"))

import OpenGL.GL as GL
import glfw as GLFW

from pyglm.glm import vec3, sin
from resources.scripts.shader import Shader, ShaderBuilder
from resources.scripts.verticeMesh import VerticeMesh
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.camera.camera3d import Camera3D
from resources.scripts.glfwUtilities import getKeyPressed
from resources.scripts.object import Obj, VerticeModelObject, Skybox
from resources.scripts.window.mouseHandler import MouseHandler
from resources.scripts.gameWindow import GameWindow, default_window_hints, WindowHints

class CoolWindow(GameWindow):
    skybox   : Skybox
    objects  : dict[int, dict[str,Obj]]
    shaders  : list[Shader]
    def __init__(self, resolution: tuple[int, int] = (800, 600)):
        hints: WindowHints = default_window_hints()
        hints.viewport = resolution
        super().__init__(hints)
        self.objects  : dict[int, dict[str,Obj]]    = {x: {} for x in range(-100,101)}
        self.shaders  : list[Shader] = []

    def update(self, deltatime: float):
        self.objects[-1]["wall1"].transform.position.x = 2 * (sin(self._time.total))
        self.objects[-3]["mover"].transform.position.x = 3 + (10 * (sin(2 * self._time.total)))
        for layer, objs in self.objects.items():
            lockedObjects = {
                key: val
                for key, val in objs.items()
                if val.flags.get('locked') is True
            }

            # Apply physics (gravity, motion)
            for obj in objs.values():
                if not obj.flags.get("locked"):
                    obj.posVel.y -= 0.1

            # Resolve collisions
            for on, obj in objs.items():
                if not obj.flags.get("locked"):
                    for ln, lo in lockedObjects.items():
                        collision, mtv = getTransformAABBCollision(obj.transform, lo.transform)
                        if collision:
                            print(f"{on} colide with {ln}! need {mtv} to correct!")
                            obj.transform.position -= 1* mtv  # Apply MTV to resolve the collision
                            obj.posVel -= 5 * mtv

            # Bound checking
            for obj in objs.values():
                if not obj.flags.get("locked"):
                    if obj.transform.position.y < -5:
                        obj.setPos(vec3(0,5,0))


            # Update object states
            for obj in objs.values():
                obj.update(deltatime)

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

        # set skybox position here because it will lag behind the camera if you dont
        self.skybox.transform.position = self.camera.position
        self.skybox.update(deltatime)

    def on_init(self):
        super().on_init()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA);
        self.skybox = Skybox(vec3(0), vec3(0), "resources/textures/skyboxes/mountain2.png")
        self.skybox.rotVel.y = 1
        block = VerticeModel(
            {"vertices":
                VerticeMesh(
                    [
                        -0.5,-.5,
                         0.5,-.5,
                         0.5, .5,
                         -0.5,-.5,
                         0.5, .5,
                         -0.5, .5,
                ]
            ),
            "colors":
                VerticeMesh(
                    [
                        0,0,1,
                        0,1,0,
                        1,0,0,
                        0,0,1,
                        0,1,0,
                        1,0,0,
                    ]
                )
            }
        )
        self.objects[-3]["terrain1"] = (
            VerticeModelObject(
                block,
                vec3(0,0,0),
                vec3(0),
                (
                    ShaderBuilder(
                        "resources/shaders/test.vert",
                        "resources/shaders/test.frag",
                        2),
                    [
                        (0, 2),
                        (1, 3)
                    ]
                ),
                True
            )
        )
        self.objects[-3]["mover"] = (
            VerticeModelObject(
                block,
                vec3(0,1,0),
                vec3(0),
                (
                    ShaderBuilder(
                        "resources/shaders/test.vert",
                        "resources/shaders/test.frag",
                        2),
                    [
                        (0, 2),
                        (1, 3)
                    ]
                ),
                True
            )
        )
        self.objects[-4]["terrain2"] = (
            VerticeModelObject(
                block,
                vec3(0,1,0),
                vec3(0),
                (
                    ShaderBuilder(
                        "resources/shaders/test.vert",
                        "resources/shaders/test.frag",
                        2),
                    [
                        (0, 2),
                        (1, 3)
                    ]
                ),
                True
            )
        )
        self.objects[-1]["wall1"] = (
            VerticeModelObject(
                block,
                vec3(0,1,0),
                vec3(0),
                (
                    ShaderBuilder(
                        "resources/shaders/test.vert",
                        "resources/shaders/test.frag",
                        2),
                    [
                        (0, 2),
                        (1, 3)
                    ]
                ),
                True
            )
        )
        self.objects[-3]["box"] = (
            VerticeModelObject(
                VerticeModel(
                    {"vertices":
                        VerticeMesh(
                            [
                                -1, -1,
                                 1, -1,
                                 1,  1,
                                -1, -1,
                                 1,  1,
                                -1,  1
                        ]
                    ),
                    "colors":
                        VerticeMesh(
                            [
                                1.000, 0.984, 0.902,
                                1.000, 0.984, 0.902,
                                1.000, 0.984, 0.902,
                                1.000, 0.984, 0.902,
                                1.000, 0.984, 0.902,
                                1.000, 0.984, 0.902
                            ]
                        )
                    }
                ),
                vec3(0,2,0),
                vec3(0),
                (
                    ShaderBuilder(
                        "resources/shaders/test.vert",
                        "resources/shaders/test.frag",
                        2),
                    [
                        (0, 2),
                        (1, 3)
                    ]
                )
            )
        )
        self.objects[-4]["terrain2"].transform.scale = vec3(100,10,1)
        self.objects[-3]["terrain1"].transform.scale = vec3(100,1,1)
        self.objects[-3]["mover"].transform.scale = vec3(1,5,1)
        self.objects[-1]["wall1"].transform.scale = vec3(2,10,1)
        self.mouseHandler = MouseHandler()
        self.camera = Camera3D(move_speed=20, far=1000)

    def render(self):
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT) # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT) # clear the color buffer
        cameraProj = self.camera.getProjectionMatrix()
        cameraView = self.camera.getViewMatrix()
        self.skybox.shader.activate()
        self.skybox.shader.setMat4fv("projection", cameraProj)
        self.skybox.shader.setMat4fv("view", cameraView)
        self.skybox.draw()
        for layer, objs in self.objects.items():
            for name, o in objs.items():
                o.shader.activate()
                o.shader.setMat4fv("projection", cameraProj)
                o.shader.setMat4fv("view", cameraView)
                o.shader.setVec3f("fogColor", 0.969, 0.969, 0.969)
                o.shader.setFloat("fogDensity", .001)
                o.shader.setFloat("layer", float(layer))
                o.draw()

    def on_key(self, key, scancode, action, mods):
        if key == GLFW.KEY_ESCAPE and action == GLFW.PRESS:
            self.set_should_close(True)
        elif action == GLFW.PRESS:
            if key == GLFW.KEY_MINUS:
                self.set_cursor_mode(GLFW.CURSOR_NORMAL)
                self.mouseHandler.set_first_mouse(True)
            if key == GLFW.KEY_EQUAL:
                self.set_cursor_mode(GLFW.CURSOR_DISABLED)
            if key == GLFW.KEY_LEFT:
                self.objects[-3]["box"].posVel.x -= 5
            if key == GLFW.KEY_RIGHT:
                self.objects[-3]["box"].posVel.x += 5
            if key == GLFW.KEY_UP:
                self.objects[-3]["box"].posVel.y += 5

    def on_resize(self, width, height):
        GL.glViewport(0, 0, width, height)
        self.camera.set_aspect_ratio(width / height)

    def on_mouse_move(self, xoffset, yoffset):
        if self.get_cursor_mode() == GLFW.CURSOR_DISABLED:
            self.mouseHandler.update(xoffset, yoffset)
            self.camera.process_mouse(self.mouseHandler.x_offset, self.mouseHandler.y_offset)

    def on_scroll(self, xoffset, yoffset):
        self.camera.process_scroll(yoffset)

if __name__ == "__main__":
    cool_window = CoolWindow((1920, 1080))
    cool_window.run()

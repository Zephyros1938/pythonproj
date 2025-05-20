import lib
from resources.scripts.physics.transform import getAABBCollision, AABBCollisionDirection
lib.init(debug=True, debugLibInternals=True)
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "ERROR"))

import OpenGL.GL as GL
import glfw as GLFW

from pyglm.glm import vec3, sin, cos, tan
from resources.scripts.shader import Shader
from resources.scripts.glfwUtilities import getKeyPressed
from resources.scripts.verticeMesh import VerticeMesh
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.camera.camera3d import Camera3D
from resources.scripts.object import Obj, Skybox, simpleRectangle
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
        self.canJump = True

    def update(self, deltatime: float):
        self.objects[-3]["mover"].transform.position.x =  60 + (5  * (cos(1 * self._time.total)))
        self.objects[-3]["mover"].transform.position.y =  10 + (15 * (sin(1 * self._time.total)))
        for layer, objs in self.objects.items():
            lockedObjects = {
                key: val
                for key, val in objs.items()
                if val.flags.get('locked') is True
            }

            # Apply physics (gravity, motion)
            for name, obj in objs.items():
                if not obj.flags.get("locked"):
                    obj.posVel.y -= 0.25

            # Resolve collisions
            for on, obj in objs.items():
                if not obj.flags.get("locked"):
                    for ln, lo in lockedObjects.items():
                        collision, mtv, dir = getAABBCollision(obj.transform, lo.transform)
                        if collision:
                            print(f"{on} colide with {ln} at {dir}!")
                            obj.transform.position -= 1* mtv  # Apply MTV to resolve the collision
                            obj.posVel -= 5 * mtv
                        if dir == AABBCollisionDirection.BOTTOM and not self.canJump:
                            self.canJump = True


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

        # if getKeyPressed(self.handle, GLFW.KEY_A):
        #     self.camera.process_keyboard(2, deltatime)
        # if getKeyPressed(self.handle, GLFW.KEY_D):
        #     self.camera.process_keyboard(3, deltatime)
        # if getKeyPressed(self.handle, GLFW.KEY_SPACE):
        #     self.camera.process_keyboard(7, deltatime)
        # if getKeyPressed(self.handle, GLFW.KEY_LEFT_CONTROL):
        #     self.camera.process_keyboard(6, deltatime)
        self.camera.position.xy = self.objects[-3]["player"].transform.position.xy

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
        block_gray = VerticeModel(
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
                        0.25,0.25,0.3,
                        0.25,0.25,0.3,
                        0.25,0.25,0.3,
                        0.25,0.25,0.3,
                        0.25,0.25,0.3,
                        0.25,0.25,0.3,
                    ]
                )
            })
        player_vm = VerticeModel(
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
            })
        self.objects[-3]["floor1"] = simpleRectangle(block_gray, pos=vec3(0,-5,0),scale=vec3(100,10,1))
        self.objects[-3]["floor2"] = simpleRectangle(block_gray, pos=vec3(0,15,0),scale=vec3(100,10,1))
        self.objects[-3]["wall1"] = simpleRectangle(block_gray, pos=vec3(-45,5,0),scale=vec3(10,30,1))
        self.objects[-3]["wall2"] = simpleRectangle(block_gray, pos=vec3(75,5,0),scale=vec3(10,30,1))
        self.objects[-3]["mover"] = simpleRectangle(block_gray, pos=vec3(55,20,0),scale=vec3(10,10,1))
        self.objects[-3]["player"] = simpleRectangle(player_vm, pos=vec3(0,2,0), locked=False)
        self.mouseHandler = MouseHandler()
        self.camera = Camera3D(move_speed=20, far=1000, position=vec3(0,0,15))
        # print(self.objects)

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
                o.shader.setFloat("fogDensity", .025)
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
                self.objects[-3]["player"].posVel.x -= 5
            if key == GLFW.KEY_RIGHT:
                self.objects[-3]["player"].posVel.x += 5
            if key == GLFW.KEY_UP:
                if self.canJump:
                    self.objects[-3]["player"].posVel.y += 25
                    self.canJump = False

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
    cool_window = CoolWindow((800, 600))
    cool_window.run()

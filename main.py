
import lib
lib.init(debug=True, debugLibInternals=True)
logger = lib.getlib("logger")
logger.init(lib.getEnumV("logger", "LEVELS", "TRACE"))
from resources.scripts.constants import MATH as MATH_CONSTANTS
from resources.scripts.gameWindow import GameWindow, default_window_hints, WindowHints
from resources.scripts.window.mouseHandler import MouseHandler
from resources.scripts.shader import ShaderBuilder
from resources.scripts.object import VerticeModelObject, Obj, Skybox, simpleRectangle, PlayerObj2D
from resources.scripts.camera.camera3d import Camera3D
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.verticeMesh import VerticeMesh
from resources.scripts.glfwUtilities import getKeyPressed
from resources.scripts.shader import Shader
from pyglm.glm import vec3, sin, cos, tan, length, exp, vec2, mix, pi
import glfw as GLFW
import OpenGL.GL as GL
from resources.scripts.physics.transform import getAABBCollision, AABBCollisionDirection





class CoolWindow(GameWindow):
    skybox: Skybox
    player: PlayerObj2D
    objects: dict[int, dict[str, Obj]]
    shaders: list[Shader]

    def __init__(self, resolution: tuple[int, int] = (800, 600)):
        hints: WindowHints = default_window_hints()
        hints.viewport = resolution
        super().__init__(hints)
        self.objects: dict[int, dict[str, Obj]] = {x: {} for x in range(-5, 6)}
        self.shaders: list[Shader] = []
        self.spawnPos = vec3(0, 5, 0)

    def update(self, deltatime: float):
        self.objects[0]["mover"].transform.position.x = 60 + \
            (5 * (sin(1 * self._time.total + MATH_CONSTANTS.HALF_PI)))
        self.objects[0]["mover"].transform.position.y = 10 + \
            (15 * (sin(1 * self._time.total)))
        self.objects[0]["mover2"].transform.position.y = 30 + \
            (15 * (sin(1 * self._time.total + MATH_CONSTANTS.TWO_THIRD_PI)))
        self.objects[0]["mover3"].transform.position.x = 70 + \
            (15 * (sin(1 * self._time.total + MATH_CONSTANTS.PI)))
        self.objects[0]["mover3"].transform.position.y = 50 + \
            (5 * (sin(1 * self._time.total)))
        self.objects[0]["mover4"].transform.position.x = -45 + \
            (60 * (2 + sin(1 * self._time.total + MATH_CONSTANTS.PI)))
        print(f"FPS: {1/deltatime:>9.4f}")
        for layer, objs in self.objects.items():
            lockedObjects = {
                key: val
                for key, val in objs.items()
                if val.flags.get('locked') is True
            }

            # Apply physics (gravity, motion)
            for name, obj in objs.items():
                if not obj.flags.get("locked"):
                    obj.posVel.y -= 0.45

            # Resolve collisions
            for on, obj in objs.items():
                if not obj.flags.get("locked"):
                    for ln, lo in lockedObjects.items():
                        collision, mtv, dir = getAABBCollision(
                            obj.transform, lo.transform)
                        if collision:
                            obj.transform.position.xy -= mtv.xy  # Apply MTV to resolve the collision
                            obj.posVel.xy -=  mtv.xy

            for ln, lo in lockedObjects.items():
                collision, mtv, dir = getAABBCollision(
                    self.player.transform, lo.transform)
                if collision:
                    # print(f"{on} colide with {ln} at {dir}!")
                    self.player.setPos(
                        vec3(self.spawnPos.x, self.spawnPos.y, self.spawnPos.z))
                    self.player.posVel = vec3(0)
                    self.player.transform.position.xy -= mtv.xy  # Apply MTV to resolve the collision
                    self.player.posVel.xy -=  mtv.xy
                if dir == AABBCollisionDirection.BOTTOM and not self.player.canJump:
                    self.player.canJump = True

            # Bound checking
            for obj in objs.values():
                if not obj.flags.get("locked"):
                    if obj.transform.position.y < -50:
                        obj.setPos(
                            vec3(self.spawnPos.x, self.spawnPos.y, self.spawnPos.z))
                        obj.posVel = vec3(0)

            # Update object states
            for obj in objs.values():
                obj.update(deltatime)

        self.player.posVel.y -= 0.45
        self.player.update(deltatime)

        if getKeyPressed(self.handle, GLFW.KEY_UP):
            self.camera.process_keyboard(0, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_DOWN):
            self.camera.process_keyboard(1, deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_A):
            self.player.moveInDir(deltatime, vec3(1,0,0))
        if getKeyPressed(self.handle, GLFW.KEY_D):
            self.player.moveInDir(deltatime, vec3(-1,0,0))
        if getKeyPressed(self.handle, GLFW.KEY_SPACE):
            self.player.jump(deltatime)
        if getKeyPressed(self.handle, GLFW.KEY_R):
            self.player.setPos(
                vec3(self.spawnPos.x, self.spawnPos.y, self.spawnPos.z))
            self.player.posVel = vec3(0)

        # Interpolates between camera's and player's positions, so no snappy movement
        self.camera.position.xy = mix(
            self.camera.position.xy,  # current
            self.player.transform.position.xy,  # target
            0.075  # lerp factor
        )

        # set skybox position here because it will lag behind the camera if you dont
        self.skybox.transform.position = self.camera.position
        self.skybox.update(deltatime)

    def on_init(self):
        super().on_init()
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # maybe use from https://mega.nz/folder/lvUSxaLA#9KIzwKK2LDNrsIpG9K0DZA
        self.skybox = Skybox(vec3(0), vec3(
            0), "resources/textures/skyboxes/high_quality/sky1.png")
        self.skybox.rotVel.y = 1
        block_gray = VerticeModel(
            {"vertices":
                VerticeMesh(
                    [
                        -0.5, -.5,
                        0.5, -.5,
                        0.5, .5,
                        -0.5, -.5,
                        0.5, .5,
                        -0.5, .5,
                    ]
                ),
                "colors":
                VerticeMesh(
                    [
                        0.25, 0.25, 0.3,
                        0.25, 0.25, 0.3,
                        0.325, 0.325, 0.37,
                        0.25, 0.25, 0.3,
                        0.325, 0.325, 0.37,
                        0.325, 0.325, 0.37,
                    ]
                )
             })
        player_vm = VerticeModel(
            {"vertices":
                VerticeMesh(
                    [
                        -0.5, -.5,
                        0.5, -.5,
                        0.5, .5,
                        -0.5, -.5,
                        0.5, .5,
                        -0.5, .5,
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
        mover_vm = VerticeModel(
            {"vertices":
                VerticeMesh(
                    [
                        -0.5, -.5,
                        0.5, -.5,
                        0.5, .5,
                        -0.5, -.5,
                        0.5, .5,
                        -0.5, .5,
                    ]
                ),
                "colors":
                VerticeMesh(
                    [
                        0.25, 0.25, 0.6,
                        0.25, 0.25, 0.6,
                        0.35, 0.35, 0.7,
                        0.25, 0.25, 0.6,
                        0.35, 0.35, 0.7,
                        0.35, 0.35, 0.7,
                    ]
                )
             })
        kill_vm = VerticeModel(
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
                        1.000, 0.0, 0.0,
                        1.000, 0.0, 0.0,
                        1.000, 0.0, 0.0,
                        1.000, 0.0, 0.0,
                        1.000, 0.0, 0.0,
                        1.000, 0.0, 0.0
                    ]
                )
             })
        self.objects[0]["floor1"] = simpleRectangle(
            block_gray, pos=vec3(0, -5, 0), scale=vec3(100, 10, 1))
        self.objects[0]["floor2"] = simpleRectangle(
            block_gray, pos=vec3(0, 35, 0), scale=vec3(100, 50, 1))
        self.objects[0]["kill"] = simpleRectangle(kill_vm, pos=vec3(
            60, -11, 0), scale=vec3(20, 1, 1), flags={"kill": True})
        self.objects[0]["kill2"] = simpleRectangle(kill_vm, pos=vec3(
            -5, 70, 0), scale=vec3(10, 10, 1), flags={"kill": True})
        self.objects[0]["wall1"] = simpleRectangle(
            block_gray, pos=vec3(-45, 5, 0), scale=vec3(10, 30, 1))
        self.objects[0]["wall2"] = simpleRectangle(
            block_gray, pos=vec3(75, 5, 0), scale=vec3(10, 30, 1))
        self.objects[0]["mover"] = simpleRectangle(
            mover_vm, pos=vec3(55, 20, 0), scale=vec3(10, 10, 1))
        self.objects[0]["mover2"] = simpleRectangle(
            mover_vm, pos=vec3(95, 15, 0), scale=vec3(10, 10, 1))
        self.objects[0]["mover3"] = simpleRectangle(
            mover_vm, pos=vec3(95, 30, 0), scale=vec3(10, 10, 1))
        self.objects[0]["mover4"] = simpleRectangle(
            mover_vm, pos=vec3(10, 70, 0), scale=vec3(20, 20, 1))
        self.player = PlayerObj2D(
            shaderBuilderInfo=(
                ShaderBuilder(
                    "resources/shaders/test.vert",
                    "resources/shaders/test.frag",
                    2),
                [(0, 2),
                 (1, 3)]
            ),
            vm=player_vm,
            locked=False,
            pos=vec3(0, 2, 0),
            rot=vec3(0),
            scale=vec3(2.5, 2.5, 1),
            flags={"player": True}
        )
        self.mouseHandler = MouseHandler()
        self.camera = Camera3D(move_speed=20, far=1000,
                               position=vec3(0, 0, 30), zoom=75)
        # print(self.objects)

    def render(self):
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)  # clear the depth buffer (3d)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)  # clear the color buffer
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
        self.player.shader.activate()
        self.player.shader.setMat4fv("projection", cameraProj)
        self.player.shader.setMat4fv("view", cameraView)
        self.player.shader.setVec3f("fogColor", 0.969, 0.969, 0.969)
        self.player.shader.setFloat("fogDensity", .001)
        self.player.shader.setFloat("layer", 0)
        self.player.draw()

    def on_key(self, key, scancode, action, mods):
        if key == GLFW.KEY_ESCAPE and action == GLFW.PRESS:
            self.set_should_close(True)
        elif action == GLFW.PRESS:
            if key == GLFW.KEY_MINUS:
                self.set_cursor_mode(GLFW.CURSOR_NORMAL)
                self.mouseHandler.set_first_mouse(True)
            if key == GLFW.KEY_EQUAL:
                self.set_cursor_mode(GLFW.CURSOR_DISABLED)

    def on_resize(self, width, height):
        GL.glViewport(0, 0, width, height)
        self.camera.set_aspect_ratio(width / height)

    def on_mouse_move(self, xoffset, yoffset):
        if self.get_cursor_mode() == GLFW.CURSOR_DISABLED:
            self.mouseHandler.update(xoffset, yoffset)
            self.camera.process_mouse(
                self.mouseHandler.x_offset, self.mouseHandler.y_offset)

    def on_scroll(self, xoffset, yoffset):
        self.camera.process_scroll(yoffset)


if __name__ == "__main__":
    cool_window = CoolWindow((1280, 720))
    cool_window.run()

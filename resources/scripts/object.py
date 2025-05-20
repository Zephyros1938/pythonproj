from typing import Union
from pyglm.glm import vec3, length, exp
import OpenGL.GL as GL
from resources.scripts.texture import Texture
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.shader import Shader, ShaderBuilder
from resources.scripts.physics.transform import Transform
from numpy import array as nparray, float32
import ctypes
from os import path as ospath

# most skyboxes from https://www.application-systeme.fr/wp-content/plugins/canvasio3dpro/inc/resource/cubeMaps/

class Obj:
    transform: Transform
    posVel: vec3
    rotVel: vec3
    shader: Shader
    vao: int
    flags: dict[str, Union[str, int, float, bool]]
    def __init__(self, pos: vec3, rot: vec3, shaderName: str,locked=False, flags = {}):
        self.transform = Transform(pos, rot)
        self.posVel = vec3(0.0)
        self.rotVel = vec3(0.0)
        self.shader = Shader(
            ospath.abspath(ospath.join("resources", "shaders", shaderName + ".vert")),
            ospath.abspath(ospath.join("resources", "shaders", shaderName + ".frag"))
        )
        self.locked = locked
        self.flags = {}

    def update(self, dt: float):
        drag = 1

        self.transform.position += self.posVel * dt
        self.transform.rotation += self.rotVel * dt

        # exponential damping
        self.posVel *= exp(-drag * dt)
        self.rotVel *= exp(-drag * dt)

        if length(self.posVel) < 1e-4:
            self.posVel = vec3(0.0)
        if length(self.rotVel) < 1e-4:
            self.rotVel = vec3(0.0)

        self.transform.update_matrix()

    def draw(self, *args, **kwargs):
        raise NotImplementedError("Base Obj class cannot be drawn!")

    def setPos(self, position: vec3):
        self.transform.position = position


class VerticeModelObject(Obj):
    vm: 'VerticeModel'
    flags: dict[str, Union[str, int, float, bool]]
    def __init__(self, vm: VerticeModel, pos: vec3, shaderBuilderInfo: tuple[ShaderBuilder, list[tuple[int, int]]], locked=False, rot: vec3= vec3(0), scale = vec3(1)):
        self.transform = Transform(pos, rot)
        self.transform.scale = scale
        self.posVel = vec3(0.0)
        self.rotVel = vec3(0.0)
        self.vm = vm
        (self.shader, self.vao) = shaderBuilderInfo[0].fromVerticeModel(vm, shaderBuilderInfo[1])
        self.flags = {"locked": locked}
    def update(self, dt: float):
        drag = 1

        self.transform.position += self.posVel * dt
        self.transform.rotation += self.rotVel * dt

        # exponential damping
        self.posVel *= exp(-drag * dt)
        self.rotVel *= exp(-drag * dt)

        if length(self.posVel) < 1e-4:
            self.posVel = vec3(0.0)
        if length(self.rotVel) < 1e-4:
            self.rotVel = vec3(0.0)
        if self.posVel.y > 15:
            self.posVel.y = 15

        self.transform.update_matrix()
    def draw(self):
        self.shader.activate()
        self.shader.setMat4fv("model", self.transform.model)
        self.vm.draw(self.shader, self.vao)


class Skybox(Obj):
    vertices: list[float] = [
        # front
        -1,-1,-1, 1,-1,-1, 1, 1,-1,
        -1,-1,-1, 1, 1,-1,-1, 1,-1,
        # bottom
        -1,-1, 1, 1, 1, 1, 1,-1, 1,
        -1,-1, 1,-1, 1, 1, 1, 1, 1,

        # top
        -1,-1,-1, 1,-1, 1, 1,-1,-1,
        -1,-1,-1,-1,-1, 1, 1,-1, 1,
        # bottom
        -1, 1,-1, 1, 1,-1, 1, 1, 1,
        -1, 1,-1, 1, 1, 1,-1, 1, 1,

        # left
        -1,-1,-1,-1, 1,-1,-1, 1, 1,
        -1,-1,-1,-1, 1, 1,-1,-1, 1,
        # right
         1,-1,-1, 1, 1, 1, 1, 1,-1,
         1,-1,-1, 1,-1, 1, 1, 1, 1,
    ]
    showing: bool = True
    shader: Shader
    vao: int
    image: Texture
    flags: dict[str, Union[str, int, float, bool]]
    def __init__(self, rot:vec3, pos:vec3, imagePath: str):
        self.transform = Transform(pos, rot)
        self.posVel = vec3(0)
        self.rotVel = vec3(0)
        self.image = Texture(imagePath, min_filter=GL.GL_NEAREST_MIPMAP_NEAREST, mag_filter=GL.GL_NEAREST, wrap_s=GL.GL_CLAMP_TO_EDGE, wrap_t=GL.GL_CLAMP_TO_EDGE)
        self.flags = {"locked": True}

        texcoords = [
            # front
            0.25,1/3 ,0.5 ,1/3 ,0.5 ,2/3 ,
            0.25,1/3 ,0.5 ,2/3 ,0.25,2/3 ,

            # bottom
            1.00,1/3 ,0.75,2/3 ,0.75,1/3 ,
            1.00,1/3 ,1.00,2/3 ,0.75,2/3 ,

            # top
            0.25,1/3 ,0.50,000 ,0.50,1/3 ,
            0.25,1/3 ,0.25,000 ,0.50,000 ,

            # bottom
            0.25,2/3 ,0.50,2/3 ,0.50,1   ,
            0.25,2/3 ,0.50,1   ,0.25,1   ,

            # left
            0.25,1/3 ,0.25,2/3 ,0.00,2/3 ,
            0.25,1/3 ,0.00,2/3 ,0.00,1/3 ,

            # right
            0.50,1/3 ,0.75,2/3 ,0.50,2/3 ,
            0.50,1/3 ,0.75,1/3 ,0.75,2/3 ,
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
        GL.glVertexAttribPointer(0,3,GL.GL_FLOAT,GL.GL_FALSE,3 * ctypes.sizeof(ctypes.c_float),ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, tbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, tcarray.nbytes, tcarray, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(1,2,GL.GL_FLOAT,GL.GL_FALSE,2 * ctypes.sizeof(ctypes.c_float),ctypes.c_void_p(0 * ctypes.sizeof(ctypes.c_float)))
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        self.vao = vao
    def update(self, dt: float):
        self.transform.position += self.posVel * dt
        self.transform.rotation += self.rotVel * dt

        self.transform.update_matrix()

    def draw(self):
        GL.glDepthMask(GL.GL_FALSE)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.image.id)
        self.shader.activate()
        self.shader.setMat4fv("model", self.transform.model)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
        GL.glUseProgram(0)
        GL.glDepthMask(GL.GL_TRUE)

def simpleRectangle(vm: VerticeModel, pos: vec3, rot:vec3 = vec3(0), scale:vec3 = vec3(1), shaderName: str = "test", locked: bool = True) -> VerticeModelObject:
    return VerticeModelObject(
        shaderBuilderInfo=(
            ShaderBuilder(
                f"resources/shaders/{shaderName}.vert",
                f"resources/shaders/{shaderName}.frag",
                2),
            [
                (0, 2),
                (1, 3)
            ]
        ),
        vm=vm,
        locked=locked,
        pos=pos,
        rot=rot,
        scale=scale
    )

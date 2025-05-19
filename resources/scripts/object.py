from pyglm.glm import translate, rotate, scale, ivec2, mat4, vec2, vec3, vec4, length, sin,cos, radians, pi as PI, exp, distance
import OpenGL.GL as GL
from resources.scripts.texture import Texture
from resources.scripts.verticeModel import VerticeModel
from resources.scripts.shader import Shader
from numpy import array as nparray, float32, uint32
import ctypes

class Obj:
    pos: vec3
    rot: vec3
    posVel: vec3
    rotVel: vec3
    model: mat4

    def __init__(self, pos: vec3, rot: vec3):
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

    def draw(self, *args, **kwargs):
        raise NotImplementedError("Base Obj class cannot be drawn!")

class VerticeModelObject(Obj):
    vm: 'VerticeModel'
    def __init__(self, vm: VerticeModel, pos: vec3, rot: vec3):
        self.vm = vm
        self.pos = pos
        self.rot = rot
        self.posVel = vec3(0.0)
        self.rotVel = vec3(0.0)
        self.model = mat4(1.0)

    def draw(self, shader: Shader, vao: int):
        shader.activate()
        shader.setMat4fv("model", self.model)
        self.vm.draw(shader, vao)
class Skybox(Obj):
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
        self.model = scale(mat4(1),vec3(1000))
        self.image = Texture(imagePath, "", min_filter=GL.GL_NEAREST_MIPMAP_NEAREST, mag_filter=GL.GL_NEAREST)

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
        GL.glVertexAttribPointer(0,3,GL.GL_FLOAT,GL.GL_FALSE,3 * ctypes.sizeof(ctypes.c_float),ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, tbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, tcarray.nbytes, tcarray, GL.GL_STATIC_DRAW)
        GL.glVertexAttribPointer(1,2,GL.GL_FLOAT,GL.GL_FALSE,2 * ctypes.sizeof(ctypes.c_float),ctypes.c_void_p(0 * ctypes.sizeof(ctypes.c_float)))
        GL.glEnableVertexAttribArray(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)
        self.vao = vao
    def draw(self):
        GL.glDepthMask(GL.GL_FALSE)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.image.id)
        self.shader.activate()
        self.shader.setMat4fv("model", self.model)
        GL.glBindVertexArray(self.vao)
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 36)
        GL.glUseProgram(0)
        GL.glDepthMask(GL.GL_TRUE)
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

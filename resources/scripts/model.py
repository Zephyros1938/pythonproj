
from dataclasses import dataclass

from pyglm.glm import vec2, vec3, value_ptr

from resources.scripts.shader import Shader

@dataclass
class Vertex:
    Position: vec3
    Normal: vec3
    TexCoords: vec2

@dataclass
class Texture:
    id: int
    type: str

@dataclass
class Mesh:
    vertices: list[Vertex]
    indices: list[int]
    textures: list[Texture]

    def __init__(self, vertices: list[Vertex], indices: list[int], textures: list[Texture]):
        self.vertices = vertices
        self.indices = indices
        self.textures = textures

        self.__setupMesh()


    def draw(self, shader: Shader):
        pass

    __VAO: int
    __VBO: int
    __EBO: int

    def __setupMesh(self):
        from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBufferData, glBindVertexArray, glBindBuffer, glBufferData, glVertexAttribPointer, glEnableVertexAttribArray
        from OpenGL.GL import GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_ELEMENT_ARRAY_BUFFER
        from OpenGL.GL import GL_FLOAT, GL_FALSE
        from sys import getsizeof as sizeof
        from numpy import array, float32

        glGenVertexArrays(1, self.__VAO)
        glGenBuffers(1, self.__VBO)
        glGenBuffers(1, self.__EBO)

        glBindVertexArray(self.__VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.__VBO)

        glBufferData(GL_ARRAY_BUFFER, sizeof(Vertex) * len(self.vertices), value_ptr(self.vertices[0]), GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.__EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(int) * len(self.indices), value_ptr(self.indices[0]), GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), value_ptr(0))

        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(Vertex), value_ptr(3 * sizeof(float)))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, sizeof(Vertex), value_ptr(6 * sizeof(float)))

        glBindVertexArray(0)

@dataclass
class Model:

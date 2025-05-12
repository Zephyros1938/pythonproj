from dataclasses import dataclass
from pyglm.glm import vec2, vec3, value_ptr
from OpenGL.GL import glActiveTexture, glBindTexture, glBindVertexArray, glDrawElements
from OpenGL.GL import GL_TEXTURE0, GL_TEXTURE_2D
from OpenGL.GL import GL_TRIANGLES, GL_UNSIGNED_INT
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
        diffuseNr: int = 1;
        specularNr: int = 1;
        for i in range(len(self.textures)):
            glActiveTexture(int(GL_TEXTURE0) + i)
            number: str = ""
            name: str = self.textures[i].type
            if name=="texture_diffuse":
                number = str(diffuseNr)
                diffuseNr+=1
            elif name=="texture_specular":
                number = str(specularNr)
                specularNr+=1
            shader.setInt("material." + name + number, i)
            glBindTexture(GL_TEXTURE_2D, self.textures[i].id)
        glActiveTexture(GL_TEXTURE0)

        glBindVertexArray(self.__VAO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, 0)
        glBindVertexArray(0)

    __VAO: int
    __VBO: int
    __EBO: int

    def __setupMesh(self):
        from OpenGL.GL import glGenVertexArrays, glGenBuffers, glBindVertexArray, glBindBuffer, glBufferData, glVertexAttribPointer, glEnableVertexAttribArray
        from OpenGL.GL import GL_ARRAY_BUFFER, GL_STATIC_DRAW, GL_ELEMENT_ARRAY_BUFFER
        from OpenGL.GL import GL_FLOAT, GL_FALSE
        from sys import getsizeof as sizeof

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

from pyassimp.structs import Material as AIMaterial, Texture as AITexture, Mesh as AIMesh, Node as AINode, Scene as AIScene
from pyassimp.postprocess import aiProcess_FindInvalidData, aiProcessPreset_TargetRealtime_Quality, aiProcess_OptimizeGraph, aiProcess_Debone, aiProcess_ImproveCacheLocality, aiProcessPreset_TargetRealtime_MaxQuality, aiProcess_FindInstances, aiProcess_ValidateDataStructure, aiProcess_JoinIdenticalVertices, aiProcess_FindDegenerates, aiProcess_PreTransformVertices, aiProcess_RemoveRedundantMaterials, aiProcess_MakeLeftHanded, aiProcess_FixTexturePaths, aiProcess_OptimizeMeshes, aiProcess_OptimizeAnimations, aiProcess_FixInfacingNormals, aiProcess_GenEntityMeshes, aiProcess_ConvertToLeftHanded, aiProcess_FlipUVs, aiProcess_RemoveComponent, aiProcess_GenSmoothNormals, aiProcess_TransformUVCoords, aiProcess_SplitLargeMeshes, aiProcessPreset_TargetRealtime_Fast, aiProcess_FlipWindingOrder, aiProcess_CalcTangentSpace, aiProcess_SortByPType, aiProcess_GenUVCoords, aiProcess_GenNormals, aiProcess_Triangulate, aiProcess_EmbedTextures, aiProcess_LimitBoneWeights, aiProcess_SplitByBoneCount

__aiProcessAllowedValues = [a for a in ( __import__("pyassimp.postprocess.").locals())]

@dataclass
class Model:
    textures_loaded = list[Texture]
    meshes: list[Mesh]
    directory: str
    gammaCorrection: bool

    def __init__(self, path: str, flags: list[int]):
        self.__loadModel(path)

    def draw(self, shader: Shader):
        [m.draw(shader) for m in self.meshes]

    def __loadModel(self, path: str):
        from pyassimp import load
        with load(path) as scene:
            pass

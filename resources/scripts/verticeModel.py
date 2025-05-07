from resources.scripts.shader import Shader
from resources.scripts.verticeMesh import VerticeMesh
import OpenGL.GL as GL

class VerticeModel:
    def __init__(self, verticeMeshes: dict[str, VerticeMesh]):
        verticeLen = 0
        for i in verticeMeshes.values():
            verticeLen += i.verticeLen
        self.verticeMeshes: dict[str, VerticeMesh] = verticeMeshes
        self.verticeLen = verticeLen

    def draw(self, shader: Shader, VAO: int):
        shader.activate()
        GL.glBindVertexArray(VAO)
        GL.glDrawArrays(shader.DRAWMODE, 0, self.verticeLen)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

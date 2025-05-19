from typing import Union
from resources.scripts.shader import Shader
import OpenGL.GL as GL

class VerticeMesh:
    def __init__(self, vertices: list[Union[float, int]]):
        self.vertices = vertices
        self.verticeLen = len(vertices)
    def draw(self, shader: Shader, VAO: int):
        shader.activate()
        GL.glBindVertexArray(VAO)
        GL.glDrawArrays(shader.DRAWMODE, 0, self.verticeLen)
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)

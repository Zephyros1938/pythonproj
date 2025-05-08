from dataclasses import dataclass
from pyglm.glm import vec3, mat4

@dataclass
class Transform:
    def __init__(self, pos: vec3 = vec3(0), eulerRot: vec3 = vec3(0), scale: vec3 = vec3(1), modelMatrix: mat4 = mat4(1)):
        self.pos = pos
        self.eulerRot = eulerRot
        self.scale = scale
        self.modelMatrix = modelMatrix

@dataclass
class Entity(Transform):
    def __init__(self, path: str, gamma: bool = False):

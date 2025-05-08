from dataclasses import dataclass
from resources.scripts.scene import Transform
from pyglm.glm import vec3, tan, cross

from resources.scripts.camera.camera3d import Camera3D
#
# With help from:
#   https://learnopengl.com/Guest-Articles/2021/Scene/Frustum-Culling

@dataclass
class Plane:
    def __init__(self, normal: vec3 = vec3(0,1,0), distance = vec3(0)):
        self.normal = normal
        self.distance = distance

@dataclass
class Frustum:
    topFace: Plane
    bottomFace: Plane

    rightFace: Plane
    leftFace: Plane

    farFace: Plane
    nearFace: Plane
    def __init__(self, topFace = Plane(), bottomFace = Plane(), rightFace = Plane(), leftFace = Plane(), farFace = Plane(), nearFace = Plane()):
        self.frontFace = topFace
        self.bottomFace = bottomFace
        self.rightFace = rightFace
        self.leftFace = leftFace
        self.farFace = farFace
        self.nearFace = nearFace


def createFrustumFromCamera(cam: Camera3D, aspect: float, fovY: float, zNear: float, zFar: float):
    frustum: Frustum = Frustum()

    halfVSide: float = zFar * tan(fovY * .5)
    halfHSide: float = halfVSide * aspect
    frontMultFar: vec3 = zFar * cam.front

    frustum.nearFace = Plane(cam.position + zNear * cam.front, cam.front)
    frustum.farFace = Plane(cam.position + frontMultFar, -cam.front)
    frustum.rightFace = Plane(cam.position, cross(frontMultFar - cam.right * halfHSide, cam.up))
    frustum.leftFace = Plane(cam.position, cross(cam.up, frontMultFar + cam.right * halfHSide))
    frustum.topFace = Plane(cam.position, cross(cam.right, frontMultFar - cam.up * halfVSide))
    frustum.bottomFace = Plane(cam.position, cross(frontMultFar + cam.up * halfVSide, cam.right))

    return frustum

@dataclass
class Volume:
    def __init__(self):
        pass

    def isOnFrustum(self, camFrustum: Frustum, modelTransform: Transform):
        return False

@dataclass
class SphereVolume(Volume):
    def __init__(self):
        self.center:vec3 = vec3(0)
        self.radius:float = 0

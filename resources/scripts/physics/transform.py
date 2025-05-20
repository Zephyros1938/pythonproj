import pyglm.glm as glm

class Transform:
    def __init__(self, position=glm.vec3(0), rotation=glm.vec3(0), scale=glm.vec3(1)):
        self.position = position
        self.rotation = rotation  # Euler ang in radians
        self.scale = scale
        self.model_matrix = glm.mat4(1.0)

    def update_matrix(self):
        self.model_matrix = glm.mat4(1.0)
        self.model_matrix = glm.translate(self.model_matrix, self.position)

        # Rotation in ZYX order
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        self.model_matrix = glm.rotate(self.model_matrix, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))

        self.model_matrix = glm.scale(self.model_matrix, self.scale)

    @property
    def model(self):
        return self.model_matrix

def getTransformAABBCollision(t1: Transform, t2: Transform):
    t1_min = t1.position - t1.scale * 0.5
    t1_max = t1.position + t1.scale * 0.5
    t2_min = t2.position - t2.scale * 0.5
    t2_max = t2.position + t2.scale * 0.5

    x_overlap = min(t1_max.x, t2_max.x) - max(t1_min.x, t2_min.x)
    y_overlap = min(t1_max.y, t2_max.y) - max(t1_min.y, t2_min.y)
    z_overlap = min(t1_max.z, t2_max.z) - max(t1_min.z, t2_min.z)

    if x_overlap > 0 and y_overlap > 0 and z_overlap > 0:
        # Collision occurred, compute MTV (Minimum Translation Vector)
        min_overlap = min(x_overlap, y_overlap, z_overlap)

        if min_overlap == x_overlap:
            direction = 1 if t1.position.x < t2.position.x else -1
            return True, glm.vec3(x_overlap * direction, 0, 0)
        elif min_overlap == y_overlap:
            direction = 1 if t1.position.y < t2.position.y else -1
            return True, glm.vec3(0, y_overlap * direction, 0)
        else:
            direction = 1 if t1.position.z < t2.position.z else -1
            return True, glm.vec3(0, 0, z_overlap * direction)

    return False, glm.vec3(0)

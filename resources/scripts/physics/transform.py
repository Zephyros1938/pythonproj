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

from pyglm.glm import cos, mat4, perspective, sin, cross, normalize, vec3, radians, lookAt

class Camera3D:
    def __init__(
        self,
        position = vec3(0.0, 0.0, 3.0),
        world_up= vec3(0.0, 1.0, 0.0),
        yaw = -90.0,
        pitch = 0.0,
        mouse_sensitivity = 0.1,
        move_speed = 2.5,
        zoom = 45.0,
        constrain_pitch = True,
        aspect_ratio = 800.0 / 600.0,
        near = 0.01,
        far = 100.0
    ):
        front = getFront(yaw, pitch)
        right = cross(front, world_up)
        up = normalize(cross(right, front))

        # self variables
        self.position = position
        self.front = front
        self.up = up
        self.right = right
        self.world_up = world_up
        self.yaw = yaw
        self.pitch = pitch
        self.mouse_sensitivity = mouse_sensitivity
        self.move_speed = move_speed
        self.zoom = zoom
        self.constrain_pitch = constrain_pitch
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

    def getViewMatrix(self) -> mat4:
        return lookAt(self.position, self.position + self.front, self.up)

    def getProjectionMatrix(self) -> mat4:
        return perspective(radians(self.zoom), self.aspect_ratio, self.near, self.far)

    def process_keyboard(self, direction: int, delta_time: float):
        """
            Processes movement for the CAMERA

            Movement values:
                - 0 = forward
                - 1 = backward
                - 2 = left
                - 3 = right
                - 4 = up
                - 5 = down
                - 6 = up (world)
                - 7 = down (world)
        """
        velocity = self.move_speed * delta_time
        if direction == 0:
            self.position += self.front * velocity
        elif direction == 1:
            self.position -= self.front * velocity
        elif direction == 2:
            self.position -= self.right * velocity
        elif direction == 3:
            self.position += self.right * velocity
        elif direction == 4:
            self.position -= self.up * velocity
        elif direction == 5:
            self.position += self.up * velocity
        elif direction == 6:
            self.position -= self.world_up * velocity
        elif direction == 7:
            self.position += self.world_up * velocity

    def process_mouse(self, xoffset: float, yoffset: float):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if self.constrain_pitch:
            self.pitch = max(min(self.pitch, 89.0), -89.0)

        self.update_vectors()

    def process_scroll(self, yoffset: float):
        self.zoom -= yoffset
        self.zoom = max(min(self.zoom, 45.0), 1.0)

    def update_vectors(self):
        front = vec3(
            cos(radians(self.yaw)) * cos(radians(self.pitch)),
            sin(radians(self.pitch)),
            sin(radians(self.yaw)) * cos(radians(self.pitch))
        )
        self.front = normalize(front)
        self.right = normalize(cross(self.front, self.world_up))
        self.up = normalize(cross(self.right, self.front))

    def set_aspect_ratio_xy(self, x: float, y: float):
        self.aspect_ratio = x / y

    def set_aspect_ratio(self, aspect: float):
        self.aspect_ratio = aspect

def getFront(yaw: float, pitch: float) -> vec3:
    return normalize(
        vec3(
            cos(radians(yaw)) * cos(radians(pitch)),
            sin(radians(pitch)),
            sin(radians(yaw)) * cos(radians(pitch))
        )
    )

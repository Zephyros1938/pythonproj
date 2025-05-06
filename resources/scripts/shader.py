import OpenGL.GL as GL
from glm import vec4, mat4, value_ptr, vec3, vec2

class Shader:
    def __init__(self, vertexPath: str, fragmentPath: str, drawmode = GL.GL_TRIANGLES):
        vertexCode: str
        fragmentCode: str

        # get vertex shader code
        try:
            print(f"[INFO] Reading vertex code: {vertexPath}")
            with open(vertexPath, "r") as f:
                vertexCode = f.read()
            print(f"[INFO] Finished reading vertex code {vertexPath}")
        except:
            raise Exception(f"[ERROR] Failed to read vertex code {vertexPath}")

        # get fragment shader code
        try:
            print(f"[INFO] Reading fragment code: {fragmentPath}")
            with open(fragmentPath, "r") as f:
                fragmentCode = f.read()
            print(f"[INFO] Finished reading fragment code {fragmentPath}")
        except:
            raise Exception(f"[ERROR] Failed to read fragment code {fragmentPath}")

        # make vertex shader
        vertexShader = GL.glCreateShader(GL.GL_VERTEX_SHADER);
        GL.glShaderSource(vertexShader, vertexCode);
        GL.glCompileShader(vertexShader);
        _checkShaderCompile(vertexShader)

        # make fragment shader
        fragmentShader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER);
        GL.glShaderSource(fragmentShader, fragmentCode);
        GL.glCompileShader(fragmentShader);
        _checkShaderCompile(fragmentShader)

        # make shader program
        ID = GL.glCreateProgram();
        GL.glAttachShader(ID, vertexShader)
        GL.glAttachShader(ID, fragmentShader)
        GL.glLinkProgram(ID)
        _checkProgramLink(ID)

        # delete unecessary memory allocation (python already has enough of that lol)
        GL.glDeleteShader(vertexShader)
        GL.glDeleteShader(fragmentShader)

        self.ID = ID
        self.DRAWMODE = drawmode

    def activate(self):
        GL.glUseProgram(self.ID)

    def setBool(self, uniformName: str, value: bool):
        GL.glUniform1i(GL.glGetUniformLocation(self.ID, uniformName), value)

    def setInt(self, uniformName: str, value: int):
        GL.glUniform1i(GL.glGetUniformLocation(self.ID, uniformName), value)

    def setFloat(self, uniformName: str, value: float):
        GL.glUniform1f(GL.glGetUniformLocation(self.ID, uniformName), value)

    def setVec4f(self, uniformName: str, v0: float, v1: float, v2:float, v3: float):
        GL.glUniform4f(GL.glGetUniformLocation(self.ID, uniformName), v0, v1, v2, v3)

    def setVec4fv(self, uniformName: str, v: vec4):
        GL.glUniform4fv(GL.glGetUniformLocation(self.ID, uniformName), value_ptr(v))

    def setVec3f(self, uniformName: str, v0: float, v1: float, v2:float):
        GL.glUniform3f(GL.glGetUniformLocation(self.ID, uniformName), v0, v1, v2)

    def setVec3fv(self, uniformName: str, v: vec3):
        GL.glUniform3fv(GL.glGetUniformLocation(self.ID, uniformName), value_ptr(v))

    def setVec2f(self, uniformName: str, v0: float, v1: float):
        GL.glUniform2f(GL.glGetUniformLocation(self.ID, uniformName), v0, v1)

    def setVec2fv(self, uniformName: str, v: vec2):
        GL.glUniform2fv(GL.glGetUniformLocation(self.ID, uniformName), value_ptr(v))

    def setMat4fv(self, uniformName: str, mat: mat4):
        GL.glUniformMatrix4fv(GL.glGetUniformLocation(self.ID, uniformName), 1, GL.GL_FALSE, value_ptr(mat))



def _checkShaderCompile(shader: None):
    success = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not success:
        log_length = GL.glGetShaderiv(shader, GL.GL_INFO_LOG_LENGTH)
        if log_length > 0:
            info_log = GL.glGetShaderInfoLog(shader)
            raise Exception(f"[ERROR] Shader Compilation failed:\n{info_log.decode('utf-8')}")
        else:
            raise Exception("[ERROR] Shader Compilation failed:\nUnknown Error")
    else:
        print("[INFO] Shader Compiled Successfully")

def _checkProgramLink(program: None):
    success = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not success:
        log_length = GL.glGetProgramiv(program, GL.GL_INFO_LOG_LENGTH)
        if log_length > 0:
            info_log = GL.glGetProgramInfoLog(program)
            raise Exception(f"[ERROR] Program Linking failed:\n{info_log.decode('utf-8')}")
        else:
            raise Exception("[ERROR] Program Linking failed:\nUnknown Error")
    else:
        print("[INFO] Program Linked Successfully")

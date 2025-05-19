import OpenGL.GL as GL
from pyglm.glm import vec4, mat4, value_ptr, vec3, vec2
import ctypes
from typing import Union
import numpy as np

from lib import getlib, cstr
logger = getlib("logger")
info = logger.info
error = logger.error

class Shader:
    def __init__(self, vertexPath: str, fragmentPath: str, drawmode = GL.GL_TRIANGLES):
        vertexCode: str
        fragmentCode: str

        info(1, cstr("Creating shader"))

        # get vertex shader code
        try:
            info(2, cstr(f"Reading vertex code: {vertexPath}"))
            with open(vertexPath, "r") as f:
                vertexCode = f.read()
            info(3, cstr(f"Finished reading vertex code {vertexPath}"))
        except:
            raise Exception(f"[ERROR] Failed to read vertex code {vertexPath}")

        # get fragment shader code
        try:
            info(2, cstr(f"Reading fragment code: {fragmentPath}"))
            with open(fragmentPath, "r") as f:
                fragmentCode = f.read()
            info(3, cstr(f"Finished reading fragment code {fragmentPath}"))
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
        info(2, cstr("Successfully created shader"))

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

class ShaderBuilder:
    from resources.scripts.verticeModel import VerticeModel
    def __init__(self,vertexPath: str, fragmentPath: str, vertexSize: int, drawmode = GL.GL_TRIANGLES):
        self.shader = Shader(vertexPath, fragmentPath, drawmode)
        self.VAO = GL.glGenVertexArrays(1)
        self.VBOs: dict[str, int] = {}
        self.vertexSize = vertexSize
        self.attributeIndex = 0
    def genVBO(self, vboName: str):
        if vboName in self.VBOs:
            raise Exception(f"VBO {vboName} already generated!")
        self.VBOs[vboName] = GL.glGenBuffers(1)
        return self
    def bindVBO(self, vboName: str):
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBOs[vboName])
        self.attributeIndex = 0
        return self
    def VBOdata(self, data: list, dtype, bufferType=GL.GL_ARRAY_BUFFER):
        array = np.array(data, dtype=dtype)
        GL.glBindVertexArray(self.VAO)
        GL.glBufferData(
            bufferType,
            array.nbytes,
            array,
            GL.GL_STATIC_DRAW
        )
        GL.glBindVertexArray(0)
        return self

    def setAttribute(
            self,
            loc: int,
            dataSize: int,
            dataType=GL.GL_FLOAT,
            normalized=GL.GL_FALSE
        ):
            data_type_size = self._sizeof_gl_type(dataType)
            stride = self.vertexSize * data_type_size
            offset = self.attributeIndex * data_type_size

            GL.glBindVertexArray(self.VAO)
            GL.glVertexAttribPointer(
                loc,
                dataSize,
                dataType,
                normalized,
                stride,
                ctypes.c_void_p(offset)
            )
            GL.glEnableVertexAttribArray(loc)
            self.attributeIndex += dataSize
            GL.glBindVertexArray(0)
            return self
    def pack(self):
        GL.glBindVertexArray(0)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        if self.attributeIndex != self.vertexSize:
            print(f"[WARN] Attribute index {self.attributeIndex} does not equal Vertex Size {self.vertexSize}!\r\n\tDid you set your attributes correctly?")
        return (self.shader, self.VAO)
    def fromVerticeModel(self, model: VerticeModel, indexes: list[tuple[int, int]]):
        if len(model.verticeMeshes.items()) != len(indexes):
            raise Exception(f"model has {len(model.verticeMeshes.items())} VerticeMeshes but got indexes with length {len(indexes)}!")
        items = list(model.verticeMeshes.items())
        info(1, cstr(f"Loading VerticeModel with data length {model.verticeLen}"))
        for n in range(len(items)):
            name = items[n][0]
            vertices = items[n][1]
            attribute = indexes[n]
            info(2, cstr(f"Setting data for VerticeMesh \"{name}\" with attribute indexes {attribute}"))
            self = self.genVBO(name).bindVBO(name).VBOdata(vertices.vertices, dtype=np.float32).setAttribute(attribute[0], attribute[1])
            info(3, cstr(f"Successfully set data for VerticeMesh \"{name}\""))
        info(2, cstr("Successfully loaded model"))
        return self.pack()
    def _sizeof_gl_type(self, gl_type) -> int:
        if gl_type == GL.GL_FLOAT:
            return ctypes.sizeof(ctypes.c_float)
        elif gl_type == GL.GL_INT:
            return ctypes.sizeof(ctypes.c_int)
        elif gl_type == GL.GL_UNSIGNED_INT:
            return ctypes.sizeof(ctypes.c_uint)
        elif gl_type == GL.GL_SHORT:
            return ctypes.sizeof(ctypes.c_short)
        elif gl_type == GL.GL_UNSIGNED_SHORT:
            return ctypes.sizeof(ctypes.c_ushort)
        elif gl_type == GL.GL_BYTE:
            return ctypes.sizeof(ctypes.c_byte)
        elif gl_type == GL.GL_UNSIGNED_BYTE:
            return ctypes.sizeof(ctypes.c_ubyte)
        else:
            raise ValueError(f"Unsupported GL type: {gl_type}")
    def _infer_gl_type(self, dtype):
        if dtype == np.float32:
            return GL.GL_FLOAT
        elif dtype == np.int32:
            return GL.GL_INT
        elif dtype == np.uint32:
            return GL.GL_UNSIGNED_INT
        # Add more as needed
        else:
            raise ValueError(f"Unsupported NumPy dtype: {dtype}")


def _checkShaderCompile(shader: None):
    success = GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS)
    if not success:
        log_length = GL.glGetShaderiv(shader, GL.GL_INFO_LOG_LENGTH)
        if log_length > 0:
            info_log = GL.glGetShaderInfoLog(shader)
            raise Exception(f"[ERROR] Shader Compilation failed:\n{info_log.decode('utf-8')}")
        else:
            raise Exception("[ERROR] Shader Compilation failed:\nUnknown Error")
    # else:
        # info(1, cstr("Shader Compiled Successfully"))

def _checkProgramLink(program: None):
    success = GL.glGetProgramiv(program, GL.GL_LINK_STATUS)
    if not success:
        log_length = GL.glGetProgramiv(program, GL.GL_INFO_LOG_LENGTH)
        if log_length > 0:
            info_log = GL.glGetProgramInfoLog(program)
            raise Exception(f"[ERROR] Program Linking failed:\n{info_log.decode('utf-8')}")
        else:
            raise Exception("[ERROR] Program Linking failed:\nUnknown Error")
    # else:
        # info(1, cstr("Program Linked Successfully"))

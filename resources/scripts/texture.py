from dataclasses import dataclass
from OpenGL.GL import GL_MIRRORED_REPEAT, GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE, GL_REPEAT, GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_NEAREST, GL_NEAREST_MIPMAP_NEAREST, GL_NEAREST_MIPMAP_LINEAR, GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR_MIPMAP_LINEAR
from OpenGL.GL import glGenTextures, glBindTexture, glTexParameteri, glTexImage2D, glGenerateMipmap

from ctypes import CDLL
import os.path as op
from os import name as osname

stbi_path = op.abspath("./resources/libraries/stbi.so") if osname == "posix" else op.abspath("./resources/libraries/stbi.dll") if osname == "nt" else ""
if stbi_path=="":
    raise Exception("Could not detect OS")
try:
    stbi = CDLL(stbi_path)
except Exception as e:
    raise Exception(f"[ERROR] Could not load library '{stbi_path}' due to exception {e}")

@dataclass
class Texture:
    path: str
    type_s: str
    id: int

    def __init__(
        self,
        path: str,
        type_s: str,
        flip: bool = True,
        wrap_s: int = GL_REPEAT,
        wrap_t: int = GL_REPEAT,
        min_filter: int = GL_LINEAR_MIPMAP_LINEAR,
        mag_filter: int = GL_LINEAR
    ):
        texture: int = 0

        glGenTextures(1, texture)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_WRAP_S,
            (wrap_s if wrap_s in [GL_MIRRORED_REPEAT, GL_CLAMP_TO_EDGE] else GL_REPEAT)
        )
        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_WRAP_T,
            (wrap_t if wrap_t in [GL_MIRRORED_REPEAT, GL_CLAMP_TO_EDGE] else GL_REPEAT)
        )
        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_MIN_FILTER,
            (min_filter if min_filter in [GL_NEAREST, GL_NEAREST_MIPMAP_NEAREST, GL_NEAREST_MIPMAP_LINEAR, GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR_MIPMAP_LINEAR] else GL_LINEAR_MIPMAP_LINEAR)
        )
        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_MAG_FILTER,
            (mag_filter if mag_filter in [
                GL_NEAREST,
                GL_NEAREST_MIPMAP_NEAREST,
                GL_NEAREST_MIPMAP_LINEAR,
                GL_LINEAR_MIPMAP_NEAREST,
                GL_LINEAR_MIPMAP_LINEAR
            ] else GL_LINEAR)
        )

        try:
            width: int = 0
            height: int = 0
            nrChannels: int = 0



            # data = im.load(op.join(op.dirname(__file__), path), width, height, nrChannels, 0)

            # if not data.is_null():
            #     pass





        except Exception as e:
            raise Exception(f"[ERROR] Failed to load image '{path}' with error {e}")

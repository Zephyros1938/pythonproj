from dataclasses import dataclass
from OpenGL.GL import GL_MIRRORED_REPEAT, GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE, GL_REPEAT, GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_NEAREST, GL_NEAREST_MIPMAP_NEAREST, GL_NEAREST_MIPMAP_LINEAR, GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR_MIPMAP_LINEAR
from OpenGL.GL import glGenTextures, glBindTexture, glTexParameteri, glTexImage2D, glGenerateMipmap
from OpenGL.GL import GL_RED, GL_RG, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE, GLuint

from ctypes import CDLL, pointer, c_int, byref, c_void_p, c_char_p, c_ubyte, cast as c_cast, POINTER
import os.path as op


try:
    import os
    lib_dir = "./libraries"

    if os.name == "posix":
        stbi_path = op.abspath(op.join(lib_dir, "compiled", "stb_image", "stb_image.so"))
    elif os.name == "nt":
        stbi_path = op.abspath(op.join(lib_dir, "compiled", "stb_image", "stb_image.dll"))
    else:
        raise OSError("Unsupported operating system: " + os.name)

    stbi = CDLL(stbi_path)

except OSError as e:
    raise Exception(f"[ERROR] Could not determine correct library path: {e}")
except Exception as e:
    raise Exception(f"[ERROR] Failed to load library: {e}")

stbi.stbi_set_flip_vertically_on_load.argtypes = [c_int]
stbi.stbi_load.argtypes = [c_char_p, POINTER(c_int), POINTER(c_int), POINTER(c_int), c_int]
stbi.stbi_load.restype = POINTER(c_ubyte)
stbi.stbi_image_free.argtypes = [POINTER(c_ubyte)]
stbi.stbi_image_free.restype = None


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
        texture_id = GLuint()
        glGenTextures(1, pointer(texture_id))
        glBindTexture(GL_TEXTURE_2D, texture_id.value)

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
            (mag_filter if mag_filter == GL_NEAREST else GL_LINEAR)
        )

        try:
            width = c_int()
            height = c_int()
            nrChannels = c_int()

            stbi.stbi_set_flip_vertically_on_load(1 if flip else 0)

            data = stbi.stbi_load(
                op.abspath(path).encode("utf-8"),
                byref(width),
                byref(height),
                byref(nrChannels), 0)

            print("[INFO] Loaded image")

            if not data:
                raise ValueError("Data for image was Null!")

            print("[INFO]  Got image data")

            try:
                format = {1 : GL_RED, 2: GL_RG, 3: GL_RGB, 4: GL_RGBA}[nrChannels.value]
            except:
                raise ValueError(f"Channels for texture was {nrChannels.value}, expected 1, 2, 3, or 4!")

            print("[INFO]  Got image format")

            size = width.value * height.value * nrChannels.value

            print(f"[INFO]  Image size: {width.value}x{height.value}, Channels: {nrChannels.value}, Total size: {size}")

            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                format,
                width.value,
                height.value,
                0,
                format,
                GL_UNSIGNED_BYTE,
                c_cast(data, c_void_p)
            )
            print("[INFO]  Loaded image TexImage2D")
            glGenerateMipmap(GL_TEXTURE_2D)
            print("[INFO]  Generated Mipmap")

            stbi.stbi_image_free(data)
            self.id = texture_id.value

        except Exception as e:
            raise Exception(f"[ERROR] Failed to load image '{op.abspath(path)}' with error {e}")

        self.type_s = type_s
        self.id = texture_id.value

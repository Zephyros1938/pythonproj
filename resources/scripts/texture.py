from resources.scripts.cacheManager import cacheFileBytes, getCachedItemBytes
from dataclasses import dataclass
from OpenGL.GL import GL_MIRRORED_REPEAT, GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE, GL_REPEAT, GL_TEXTURE_WRAP_T
from OpenGL.GL import GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR, GL_NEAREST, GL_NEAREST_MIPMAP_NEAREST, GL_NEAREST_MIPMAP_LINEAR, GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR_MIPMAP_LINEAR
from OpenGL.GL import glGenTextures, glBindTexture, glTexParameteri, glTexImage2D, glGenerateMipmap
from OpenGL.GL import GL_RED, GL_RG, GL_RGB, GL_RGBA, GL_UNSIGNED_BYTE, GLuint

from ctypes import pointer
import time
import os

from lib import getlib, cstr, ffi
logger = getlib("logger")
info = logger.info
error = logger.error

stb_image = getlib("stb_image")

@dataclass
class Texture:
    path: str
    id: int

    def __init__(
        self,
        path: str,
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
            width_ptr = ffi.new("int*")
            height_ptr = ffi.new("int*")
            nrChannels_ptr = ffi.new("int*")

            stb_image.stbi_set_flip_vertically_on_load(1 if flip else 0)

            # print(os.path.abspath(path).encode("utf-8"))

            # print(cstr(os.path.abspath(path)))

            data = stb_image.stbi_load(
                cstr(os.path.abspath(path)),
                width_ptr,
                height_ptr,
                nrChannels_ptr,
                0
            )
            info(1, cstr(f"Got image: {path}"))

            width = width_ptr[0]
            height = height_ptr[0]
            nrChannels = nrChannels_ptr[0]

            info(1, cstr("Loaded image"))
            if not data:
                raise ValueError("Data for image was Null!")

            info(2, cstr("Got image data"))

            try:
                format = {1 : GL_RED, 2: GL_RG, 3: GL_RGB, 4: GL_RGBA}[nrChannels]
            except:
                raise ValueError(f"Channels for texture was {nrChannels}, expected 1, 2, 3, or 4!")

            info(2, cstr("Got image format"))

            size = width * height * nrChannels

            info(3, cstr(f"Image size: {width}x{height}, Channels: {nrChannels}, Total size: {size}"))


            try:
                dat = getCachedItemBytes(path)
                info(3, cstr("Image cached, loading"))
            except FileNotFoundError:
                info(3, cstr("Image was not cached! caching..."))
                dat = ffi.unpack(data, size)
                cacheFileBytes(path, dat)
                info(3, cstr("Image cached."))

            startProcessTime = time.time()
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                format,
                width,
                height,
                0,
                format,
                GL_UNSIGNED_BYTE,
                dat
            )
            info(2, cstr(f"Loaded image TexImage2D in {time.time()-startProcessTime:.4f}s"))
            glGenerateMipmap(GL_TEXTURE_2D)
            info(2, cstr("Generated Mipmap"))

            stb_image.stbi_image_free(data)
            self.id = texture_id.value

        except Exception as e:
            raise Exception(f"[ERROR] Failed to load image '{os.path.abspath(path)}' with error {e}")

        self.id = texture_id.value

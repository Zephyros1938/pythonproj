# shader.py

`resources/scripts/shader.py`

## Overview

The `Shader` class is used to quicken the process of compiling shaders for OpenGL, as well as managing uniform variables. It is intended to be a simple way of reducing boilerplate code and centralizing the process for OpenGL rendering

## Table of Contents

1. [Use](#use)

---

## Use

The `Shader` class is used to quicken the process of compiling shaders for OpenGL, along with setting shader uniforms (constants)

It is designed to be integrated with the GLFW Rendering pipeline.

---

## Requirements

- Python 3.10+
- PyOpenGL
- PyGlm
- A valid OpenGL context (e.g. via GLFW or Pygame)

---

## Initialization

```python
from resources.scripts.shader import Shader
import OpenGL.GL as GL

shader: Shader = Shader("path/to/your/vert/shader.vert", "path/to/your/frag/shader.frag", drawmode = GL.GL_TRIANGLES)
```

### Parameters

1. `vertexPath`: The path to your vertex shader
2. `fragmentPath`: The path to your fragment shader
3. `drawmode`: The target drawmode for drawing during the render loop (default=`GL_TRIANGLES`)

## Variables

- `ID`: The shader program's ID
- `DRAWMODE`: The shader program's drawmode

## Methods

### `activate()`

Activates the shader program for drawing or setting uniforms

### `setBool(uniformName: str, value: bool)`

Sets the target uniform `uniformName` to the specified boolean value

### `setInt(uniformName: str, value: int)`

Sets the target uniform `uniformName` to the specified integer value

### `setFloat(uniformName: str, value: float)`

Sets the target uniform `uniformName` to the specified floating-point value

### `setVec2f(uniformName: str, v0: float, v1: float)`

Sets the target uniform `uniformName` to the specified vec2 of floating-point values (v0, v1)

### `setVec3f(uniformName: str, v0: float, v1: float, v2: float)`

Sets the target uniform `uniformName` to the specified vec3 of floating-point values (v0, v1, v2)

### `setVec4f(uniformName: str, v0: float, v1: float, v2: float, v3: float)`

Sets the target uniform `uniformName` to the specified vec4 of floating-point values (v0, v1, v2, v4)

### `setVec2fv(uniformName: str, v: vec2)`

Sets the target uniform `uniformName` to the specified floating-point vec2 `v`, via a pointer.

### `setVec3fv(uniformName: str, v: vec3)`

Sets the target uniform `uniformName` to the specified floating-point vec3 `v`, via a pointer.

### `setVec4fv(uniformName: str, v: vec4)`

Sets the target uniform `uniformName` to the specified floating-point vec4 `v`, via a pointer.

### `setMat4fv(uniformName: str, mat: mat4)`

Sets the target uniform `uniformName` to the specified floating-point mat4 `mat`, via a pointer.

---

## Uniform Management

Uniforms **must** be set after the shader is activated (`activate()` called prior)
```python
from pyglm.glm import vec3

shader.activate() # Only needed once
shader.setBool("lightEnabled", True)
shader.setVec3fv("lightPosition", vec3(5,5,5))
shader.activate() # Used a second time due to setting the lightPosition uniform more than once
shader.setVec3fv("lightPosition", vec3(5,5,6))
```

---

## Error Handling

If the shader fails to compile or link, an exception is raised including log information regarding what went wrong.

Make sure that shaders compile correctly before further use.

---

## Examples

```python
from resources.scripts.shader import Shader

#
# Initializing the `view` variable
#

shader: Shader = Shader("shaders/example.vert", "shaders/example.frag")
shader.activate()
shader.setMat4fv("view", view)
```

---

## Notes

- Intended to be used on OpenGL versions 3.3+

## Changelog

### v1.0.0
- Initial release with documentation

# shader.py

`resources/scripts/shader.py`

## Overview

The `ShaderBuilder` class is used to quickly and efficiently construct the `Shader` class, used for setting shader attributes in a quick manner.

## Table of Contents

1. [Use](#use)
2. [Requirements](#requirements)
3. [Initialization](#initialization)
4. [Variables](#variables)
5. [Methods](#methods)
6. [Error Handling](#error-handling)
7. [Examples](#examples)
8. [Notes](#notes)
9. [Changelog](#changelog)

---

## Use

The `ShaderBuilder` class is used to efficiently build & pack the `Shader` class.

The `ShaderBuilder` class should not be used directly to interact with OpenGL or any rendering, rather used to create a `Shader`

---

## Requirements

- Python 3.10+
- PyOpenGL
- PyGlm
- A valid OpenGL context (e.g. via GLFW or Pygame)

---

## Initialization

```python
from resources.scripts.shader import Shader, ShaderBuilder
import OpenGL.GL as GL

shader: ShaderBuilder = ShaderBuilder("path/to/your/vert/shader.vert", "path/to/your/frag/shader.frag", vertexSize = 3, drawmode = GL.GL_TRIANGLES)
```

### Parameters

1. `vertexPath`: The path to your vertex shader
2. `fragmentPath`: The path to your fragment shader
3. `vertexSize` : The total size of each vertex
4. `drawmode`: The target drawmode for drawing during the render loop (default=`GL_TRIANGLES`)

## Variables

- `shader`: The ShaderBuilder's internal shader
- `VAO`: The bould Vertex Attribute Array.
- `VBOs`: A list of the Vertex Buffer Objects
- `vertexSize`: The total size of each vertex in the shader.
- `attributeIndex`: The index used when setting vertex attributes

## Methods

### `genVBO(vboName: str)`

Generates a VBO used for setting attributes.

### `bindVBO(self, vboName: str)`

Binds the specified VBO

### `VBOdata(data: list[float])`

Sets the specified VBO's data

### `setAttribute(loc: int, dataSize: int)`

Sets a Vertex Attribute at the specified location, with the specified datasize

### `pack()`

Packs the ShaderBuilder into a tuple of (`Shader`, VAO)

### `fromVerticeModel(model: VerticeModel, indexes: list[tuple[int, int]])`

Equivilant to ShaderBuilder.pack(), a `VerticeModel` to construct the ShaderBuilder.

Indexes is a list of tuples including (attribute position, attribute size)

---

## Error Handling

If the ShaderBuilder encounters any issues during building or packing, an exception is raised including information regarding what went wrong.

---

## Examples

```python
from resources.scripts.shader import Shader, ShaderBuilder

vertices = [
     0.0,  0.5, 0.0,
    -0.5, -0.5, 0.0,
     0.5, -0.5, 0.0
]

colors = [
    1.0, 0.0, 0.0,
    0.0, 1.0, 0.0,
    0.0, 0.0, 1.0
]

shader, vao = (
    ShaderBuilder("shaders/example.vert", "shaders/example.frag", 6) # Set the vert and frag shader sources, along with the vertexSize
    .genVBO("vertices") # Generate a VBO with the title 'vertices'
    .bindVBO("vertices") # Bind the 'vertices' VBO
    .VBOdata(vertices) # Set the bound VBO's data
    .setAttribute(0, 3) # Tell the ShaderBuilder that the position of the vertice is 0, and that the total size of it is 3
    .genVBO("colors") # Generate a VBO with the title 'colors'
    .bindVBO("colors") # Bind the 'colors' VBO
    .VBOdata(colors) # Set the bound VBO's data
    .setAttribute(1, 3) # Tell the ShaderBuilder that the position of the color vertice is 1, and that the total size of it is 3
    .pack() # Pack the ShaderBuilder into a Shader & VAO for further use in the renderloop
)
```

---

## Notes

- Intended to be used on OpenGL versions 3.3+

---

## Changelog

### v1.0.0
- Initial release with documentation

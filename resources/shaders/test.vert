#version 330 core

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec3 aColor;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float layer;

out vec3 color;
out float fragDepth;

void main() {
    vec4 viewPos = view * model * vec4(aPos, layer, 1.0);
    fragDepth = abs(viewPos.z); // Eye-space Z is negative in front of camera
    color = aColor;
    gl_Position = projection * viewPos;
}

#version 330 core

out vec4 FragColor;

in vec3 color; // Object color
in float fragDepth; // Eye-space depth

uniform vec3 fogColor; // Approximate skybox color
uniform float fogDensity; // Controls fog strength

void main() {
    float fogFactor = exp(-fogDensity * fragDepth);
    fogFactor = clamp(fogFactor, 0.0, 1.0);

    vec3 blended = mix(fogColor, color, fogFactor);
    FragColor = vec4(blended, 1.0);
}

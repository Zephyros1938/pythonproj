#version 330 core
out vec4 FragColor;
in vec2 texCoord;

uniform sampler2D texture1;

void main() {
    FragColor = texture(texture1, texCoord);
    // FragColor = vec4(texCoord, 1.0, 1.0);
}

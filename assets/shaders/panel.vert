#version 440
layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;
layout(location = 0) out vec2 qt_TexCoord0;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float progress;
    vec2 origin;
    vec2 extent;
};
void main() {
    qt_TexCoord0 = qt_MultiTexCoord0;
    // Keep every edge and glyph rigid. Faceted clipping in the fragment stage
    // reveals the surface without bending or stretching the desktop UI.
    gl_Position = qt_Matrix * qt_Vertex;
}

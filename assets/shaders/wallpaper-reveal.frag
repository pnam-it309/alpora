#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 extent;
    vec2 origin;
    float progress;
    float sourceAspect;
};
layout(binding = 1) uniform sampler2D source;
void main() {
    vec2 uv = qt_TexCoord0;
    float aspect = extent.x / max(1.0, extent.y);
    if (sourceAspect > aspect)
        uv.x = (uv.x - 0.5) * aspect / sourceAspect + 0.5;
    else
        uv.y = (uv.y - 0.5) * sourceAspect / aspect + 0.5;
    float reach = max(max(length(origin), length(extent - origin)),
                      max(length(vec2(extent.x, 0) - origin), length(vec2(0, extent.y) - origin)));
    float distanceFromDrop = length(qt_TexCoord0 * extent - origin);
    float alpha = 1.0 - smoothstep(progress * (reach + 2.0) - 1.0,
                                 progress * (reach + 2.0) + 1.0, distanceFromDrop);
    fragColor = texture(source, uv) * alpha * qt_Opacity;
}

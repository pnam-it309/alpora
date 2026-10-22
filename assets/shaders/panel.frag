#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float progress;
    vec2 origin;
    vec2 extent;
};
layout(binding = 1) uniform sampler2D source;
void main() {
    float p = clamp(progress, 0.0, 1.0);
    vec2 uv = qt_TexCoord0;
    vec4 col = texture(source, uv);
    // One smooth rounded aperture, with no hexagonal front or triangle phases.
    // Reveal the full-width search row first instead of sweeping across letters.
    float travel = 1.0 - pow(1.0 - p, 3.0);
    vec2 size = vec2(extent.x * mix(0.98, 1.0, travel), extent.y * travel);
    vec2 center = vec2(extent.x * 0.5, size.y * 0.5);
    float radius = min(26.0, min(size.x, size.y) * 0.5);
    vec2 q = abs(uv * extent - center) - size * 0.5 + radius;
    float distance = length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - radius;
    float coverage = (1.0 - smoothstep(-1.0, 1.0, distance)) * step(0.001, p);
    fragColor = col * qt_Opacity * coverage;
}

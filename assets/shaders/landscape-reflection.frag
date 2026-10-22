#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float phase;
    float motion;
};
layout(binding = 1) uniform sampler2D source;
void main() {
    vec2 uv = qt_TexCoord0;
    float depth = uv.y;
    // A small, bounded water patch: taper along both banks and fade at depth.
    float bank = smoothstep(0.0, 0.09 + depth * 0.12, uv.x)
               * smoothstep(0.0, 0.09 + depth * 0.12, 1.0 - uv.x);
    uv.x += motion * (sin(depth * 110.0 - phase * 1.3) * 0.006
                    + sin(depth * 63.0 + phase) * 0.003) * (0.25 + depth);
    uv.y = 1.0 - depth;
    float ripple = 0.74 + 0.26 * sin(depth * 240.0 + phase * motion * 2.0);
    float fade = pow(1.0 - depth, 2.1) * bank * ripple * 0.42;
    fragColor = texture(source, clamp(uv, 0.0, 1.0)) * fade * qt_Opacity;
}

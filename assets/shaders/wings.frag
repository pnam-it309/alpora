#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 1) in vec4 shapeRect;
layout(location = 2) in vec2 revealAlpha;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float visualProgress;
    vec2 extent;
    vec4 seed;
    vec4 destination;
    vec4 topColor;
    vec4 bottomColor;
    float cornerRadius;
    float revealActive;
};
layout(binding = 1) uniform sampler2D source;
void main() {
    if(revealActive<.5){fragColor=vec4(0.);return;}
    vec2 point=qt_TexCoord0*extent;
    vec4 rect=shapeRect;
    float radius=min(cornerRadius,min(rect.z,rect.w)*.5);
    vec2 q=abs(point-rect.xy-rect.zw*.5)-rect.zw*.5+radius;
    float distance=length(max(q,vec2(0.)))+min(max(q.x,q.y),0.)-radius;
    float aa=max(fwidth(distance),.75);
    float coverage=1.-smoothstep(-aa,aa,distance);
    vec2 uv=(point-destination.xy)/destination.zw;
    vec4 color=mix(topColor,bottomColor,clamp(uv.y,0.,1.));
    float border=(1.-smoothstep(.1,1.2,-distance));
    color=mix(color,vec4(.294,.345,.314,1.),border*.7);
    vec4 content=texture(source,clamp(uv,vec2(0.),vec2(1.)));
    float inside=step(0.,uv.x)*step(0.,uv.y)*step(uv.x,1.)*step(uv.y,1.);
    content*=inside*revealAlpha.y*(1.-smoothstep(-2.,0.,distance));
    color=content+color*(1.-content.a);
    float shadow=.085*exp(-max(distance,0.)/3.)*(1.-coverage);
    fragColor=(color*coverage+vec4(0.,0.,0.,shadow))*qt_Opacity*revealAlpha.x;
}

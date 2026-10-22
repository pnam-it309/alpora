#version 440
layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;
layout(location = 0) out vec2 point;
layout(location = 1) out vec4 shape;
layout(location = 2) out vec4 radii;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float visualProgress;
    vec2 extent;
    vec2 origin;
    vec4 topColor;
    vec4 bottomColor;
    vec4 edgeColor;
    float cornerRadius;
    float cornerCut;
    float edgeWidth;
    float shadowStrength;
};
float smoothest(float t) {
    t=clamp(t,0.,1.);
    return t*t*t*(10.+t*(-15.+6.*t));
}
void main() {
    float t=clamp(visualProgress,0.,1.);
    vec4 start=vec4(origin-vec2(9.,12.),18.,24.);
    // One monotone expansion: no intermediate stop or direction reversal.
    // The asymmetric corners retain the liquid character while the final
    // approach slows continuously to zero velocity.
    float expansion=1.-pow(1.-t,3.);
    shape=mix(start,vec4(0.,0.,extent),expansion);
    float halfSize=min(shape.z,shape.w)*.5;
    vec4 blob=halfSize*vec4(1.,.58,.92,.68);
    radii=mix(blob,vec4(min(cornerRadius,halfSize)),smoothest(t/.55));
    // Keep the button's x inside the body's straight top edge. A large
    // left corner otherwise shifts a left-anchored launcher's visible crest
    // toward its right side and disconnects it from the fluid neck.
    vec2 reach=max(vec2(0.),vec2(origin.x-shape.x,shape.x+shape.z-origin.x)-vec2(4.));
    radii.xw=min(radii.xw,vec2(reach.x));
    radii.yz=min(radii.yz,vec2(reach.y));
    // Include the anchored tip above the body in the moving quad's bounds.
    vec2 low=min(shape.xy,origin-vec2(10.))-vec2(10.);
    vec2 high=max(shape.xy+shape.zw,origin+vec2(10.))+vec2(10.);
    point=mix(low,high,qt_MultiTexCoord0);
    gl_Position=qt_Matrix*vec4(point,qt_Vertex.z,qt_Vertex.w);
}

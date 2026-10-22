#version 440
layout(location = 0) in vec4 qt_Vertex;
layout(location = 1) in vec2 qt_MultiTexCoord0;
layout(location = 0) out vec2 qt_TexCoord0;
layout(location = 1) out vec4 shapeRect;
layout(location = 2) out vec2 revealAlpha;
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
float settle(float t) { t=clamp(t,0.,1.); return t*t*t*(10.+t*(-15.+6.*t)); }
vec4 tangent(vec4 a,vec4 b,float h0,float h1) {
    vec4 safeA=mix(vec4(1.),a,greaterThan(abs(a),vec4(.00001)));
    vec4 safeB=mix(vec4(1.),b,greaterThan(abs(b),vec4(.00001)));
    vec4 denom=(2.*h1+h0)/safeA+(h1+2.*h0)/safeB;
    denom=mix(vec4(1.),denom,greaterThan(abs(denom),vec4(.00001)));
    return mix(vec4(0.),vec4(3.*(h0+h1))/denom,greaterThan(a*b,vec4(0.)));
}
vec4 geometry(float u) {
    float center=clamp(seed.x+seed.z*.5,destination.x+24.,destination.x+destination.z-24.);
    vec4 a=seed,b=vec4(center-15.,destination.y,30.,destination.w),c=destination;
    vec4 d0=(b-a)/.34,d1=(c-b)/.50,d2=vec4(0.);
    vec4 m1=tangent(d0,d1,.34,.50),m2=vec4(0.);
    float t,h;vec4 p,q,m,n;
    if(u<=.34){t=u/.34;h=.34;p=a;q=b;m=d0;n=m1;}
    else if(u<=.84){t=(u-.34)/.50;h=.50;p=b;q=c;m=m1;n=m2;}
    else{return c;}
    float t2=t*t,t3=t2*t;
    return (2.*t3-3.*t2+1.)*p+(t3-2.*t2+t)*h*m+(-2.*t3+3.*t2)*q+(t3-t2)*h*n;
}
void main() {
    float t=clamp(visualProgress,0.,1.);
    shapeRect=geometry(settle(t));
    revealAlpha=vec2(settle(t/.10),settle((shapeRect.z/destination.z-.08)/.7));
    // Rasterize only the moving glass and its small shadow. The fixed content
    // texture keeps its final dimensions; no text is resized or reflowed.
    vec2 point=shapeRect.xy-vec2(9.)+qt_MultiTexCoord0*(shapeRect.zw+vec2(18.));
    qt_TexCoord0=point/extent;
    gl_Position=qt_Matrix*vec4(point,qt_Vertex.z,qt_Vertex.w);
}

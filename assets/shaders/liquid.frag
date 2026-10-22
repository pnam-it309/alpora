#version 440
layout(location = 0) in vec2 point;
layout(location = 1) in vec4 shape;
layout(location = 2) in vec4 radii;
layout(location = 0) out vec4 fragColor;
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
void main() {
    vec2 p=point-shape.xy-shape.zw*.5;
    float radius=p.y<0. ? (p.x<0. ? radii.x:radii.y) : (p.x<0. ? radii.w:radii.z);
    vec2 q=abs(p)-shape.zw*.5+radius;
    float d=length(max(q,vec2(0.)))+min(max(q.x,q.y),0.)-radius;
    // Settle into a softly bevelled Alpine outline on the hover panel only.
    vec2 cutBox=abs(p)-shape.zw*.5+vec2(1.5);
    float cut=min(cornerCut,min(shape.z,shape.w)*.25);
    float bevel=max(max(cutBox.x,cutBox.y),(cutBox.x+cutBox.y+cut)*.70710678)-1.5;
    d=mix(d,bevel,step(.01,cornerCut)*smoothstep(.48,.95,visualProgress));
    // A narrow fluid neck stays pinned to the actual bar button while the
    // body grows underneath it. It merges back into the panel near the end.
    float weight=1.-smoothstep(.72,1.,visualProgress);
    vec2 neckEnd=vec2(origin.x,max(origin.y,shape.y+min(cornerRadius,shape.w*.5)));
    vec2 segment=neckEnd-origin;
    float along=clamp(dot(point-origin,segment)/max(dot(segment,segment),.001),0.,1.);
    float neck=length(point-origin-segment*along)-mix(3.,11.,along);
    float blend=12.;
    float h=clamp(.5+.5*(neck-d)/blend,0.,1.);
    float joined=mix(neck,d,h)-blend*h*(1.-h);
    d=mix(d,joined,weight);
    float aa=max(fwidth(d),.65);
    float coverage=1.-smoothstep(-aa,aa,d);
    vec4 color=mix(topColor,bottomColor,clamp(point.y/extent.y,0.,1.));
    float border=(1.-smoothstep(max(0.,edgeWidth-0.85),edgeWidth+0.3,-d))*.7*step(.01,edgeWidth);
    color=mix(color,edgeColor,border);
    // QML colors are straight alpha; ShaderEffect output must be premultiplied.
    color.rgb*=color.a;
    float shadow=.085*shadowStrength*exp(-max(d,0.)/3.)*(1.-coverage);
    float alpha=smoothstep(0.,.10,visualProgress);
    fragColor=(color*coverage+vec4(0.,0.,0.,shadow))*qt_Opacity*alpha;
}

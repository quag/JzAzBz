// Author: Quag <quaggy@gmail.com
// Title: Quag's jchz color space (based on the JzAzBz) - trivial implementation

#ifdef GL_ES
precision mediump float;
#endif

uniform vec2 u_resolution;

float lms(float t) {
    if (t > 0.) {
        float r = pow(t, 0.007460772656268214);
        float s = (0.8359375 - r) / (18.6875*r + -18.8515625);
        return pow(s, 6.277394636015326);
    } else {
        return 0.;
    }
}

float srgb(float c) {
    if (c <= 0.0031308049535603713) {
        return c * 12.92;
    } else {
        float c_ = pow(c, 0.41666666666666666);
        return c_ * 1.055 + -0.055;
    }
}

vec3 jchz2srgb(vec3 jchz) {
    float jz = jchz.x*0.16717463120366200 + 1.6295499532821566e-11;
    float cz = jchz.y*0.16717463120366200;
    float hz = jchz.z*6.28318530717958647 + -3.14159265358979323;
    
    float iz = jz / (0.56*jz + 0.44);
    float az = cz * cos(hz);
    float bz = cz * sin(hz);
    
    float l_ = iz + az* +0.13860504327153930 + bz* +0.058047316156118830;
    float m_ = iz + az* -0.13860504327153927 + bz* -0.058047316156118904;
    float s_ = iz + az* -0.09601924202631895 + bz* -0.811891896056039000;
    
    float l = lms(l_);
    float m = lms(m_);
    float s = lms(s_);
    
    float lr = l* +0.0592896375540425100e4 + m* -0.052239474257975140e4 + s* +0.003259644233339027e4;
    float lg = l* -0.0222329579044572220e4 + m* +0.038215274736946150e4 + s* -0.005703433147128812e4;
    float lb = l* +0.0006270913830078808e4 + m* -0.007021906556220012e4 + s* +0.016669756032437408e4;
    
    return vec3(srgb(lr), srgb(lg), srgb(lb));
}

void main() {
	vec2 st = gl_FragCoord.xy/u_resolution;
	gl_FragColor = vec4(jchz2srgb(vec3(st.y, 0.2, st.x)),1.0);
}


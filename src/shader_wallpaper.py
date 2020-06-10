from gi.repository import Gtk, Gdk

from OpenGL.GL import (glBufferData, glLinkProgram,
                       glGenVertexArrays, glUseProgram,
                       glBindVertexArray, glBindBuffer,
                       glGetAttribLocation, glGetUniformLocation,
                       glGenBuffers, glEnableVertexAttribArray,
                       glClear, glFlush, glVertexAttribPointer,
                       glDrawArrays, glDisableVertexAttribArray,
                       glUniform1f, GL_FRAGMENT_SHADER,
                       GL_VERTEX_SHADER, GL_ARRAY_BUFFER,
                       GL_STATIC_DRAW, GL_COLOR_BUFFER_BIT,
                       GL_DEPTH_BUFFER_BIT, GL_TRIANGLES, GL_FLOAT)
# from OpenGL.GLUT import *
from OpenGL.GL import shaders

import numpy as np
import ctypes

import gi
gi.require_version('Gtk', '3.0')
gi.require_version("Gdk", "3.0")


FRAGMENT_SOURCE = """
#version 400
out vec4 fragColor;
uniform float time;
uniform vec2 resolution = vec2(1920.0, 1080.0);
varying vec3 v_color;

#define FIELD 5.0
#define ITERATION 12
#define CHANNEL bvec3(true,true,true)
#define TONE vec3(0.299,0.587,0.114)


vec3 computeColor(vec2 fx){
	vec3 color = vec3(vec3(CHANNEL)*TONE);
	color -= (fx.x);
	color.b += color.g*1.5;
	return clamp(color,(0.0),(1.0));
}


vec2 wolfFaceEQ(vec3 p,float t){
	vec2 fx = vec2(p.x, p.y);
	p=(abs(p*2.0));
	const float j=float(ITERATION);
	vec2 ab = vec2(2.0-p.x);
	for(float i=0.0; i<j; i++){
		ab+=(p.xy)-cos(length(p));
		p.y+=t*0.1 + sin(ab.x-p.z)*0.8;
		p.x+=t*0.1 + sin(ab.y)*0.9;
		p-=(p.x+p.y);
		p+=(fx.y+cos(fx.x));
		ab += vec2(p.y);
	}
	p/=FIELD;
	fx.x=(p.x+p.x+p.y);
	return fx;
}

vec3 makeShader() {
    float ratio = resolution.y/resolution.x;
    vec4 fake_FragCoord = gl_FragCoord;
    fake_FragCoord.y *= ratio;
    vec2 position = ( fake_FragCoord.xy / resolution.xy )-vec2(1.0,1.0*ratio);
    vec3 p = position.xyx*FIELD;
    p.z = 2.0*FIELD*0.5;
    vec3 result = computeColor(wolfFaceEQ(p+2.5,time));
    return result;
}

////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////

mat2 rot(in float a){float c = cos(a), s = sin(a);return mat2(c,s,-s,c);}
const mat3 m3 = mat3(0.33338, 0.56034, -0.71817, -0.87887, 0.32651, -0.15323, 0.15162, 0.69596, 0.61339)*1.93;
float mag2(vec2 p){return dot(p,p);}
float linstep(in float mn, in float mx, in float x){ return clamp((x - mn)/(mx - mn), 0., 1.); }
float prm1 = 0.;
vec2 bsMo = vec2(0);


vec2 disp(float t){ return vec2(sin(t*0.22)*1., cos(t*0.175)*1.)*2.; }

vec2 map(vec3 p)
{
    vec3 p2 = p;
    p2.xy -= disp(p.z).xy;
    p.xy *= rot(sin(p.z+time)*(0.1 + prm1*0.05) + time*0.09);
    float cl = mag2(p2.xy);
    float d = 0.;
    p *= .61;
    float z = 1.;
    float trk = 1.;
    float dspAmp = 0.1 + prm1*0.2;
    for(int i = 0; i < 4; i++)
    {
		p += sin(p.zxy*0.75*trk + time*trk*.8)*dspAmp;
        d -= abs(dot(cos(p), sin(p.yzx))*z);
        z *= 0.57;
        trk *= 0.4;
        p = p*m3;
    }
    d = abs(d + prm1*2.)+ prm1*.3 - 5.5; // + bsMo.y
    return vec2(d + cl*.2 + 0.25, cl);
}

vec4 render( in vec3 ro, in vec3 rd, float time )
{
	vec4 rez = vec4(0);
    const float ldst = 8.;
	vec3 lpos = vec3(disp(time + ldst)*0.5, time + ldst);
	float t = 1.5;
	float fogT = 0.;
	for(int i=0; i<130; i++)
	{
		if(rez.a > 0.99)break;

		vec3 pos = ro + t*rd;
        vec2 mpv = map(pos);
		float den = clamp(mpv.x-0.3,0.,1.)*1.12;
		float dn = clamp((mpv.x + 2.),0.,3.);

		vec4 col = vec4(0);
        if (mpv.x > 0.6)
        {

            col = vec4(sin(vec3(5.,0.4,0.2) + mpv.y*0.1 +sin(pos.z*0.4)*0.5 + 1.8)*0.5 + 0.5,0.08);
            col *= den*den*den;
			col.rgb *= linstep(4.,-2.5, mpv.x)*2.3;
            float dif =  clamp((den - map(pos+.8).x)/9., 0.001, 1. );
            dif += clamp((den - map(pos+.35).x)/2.5, 0.001, 1. );
            col.xyz *= den*(vec3(0.005,.045,.075) + 1.5*vec3(0.033,0.07,0.03)*dif);
        }

		float fogC = exp(t*0.2 - 2.2);
		col.rgba += vec4(0.06,0.11,0.11, 0.1)*clamp(fogC-fogT, 0., 1.);
		fogT = fogC;
		rez = rez + col*(1. - rez.a);
		t += clamp(0.5 - dn*dn*.05, 0.09, 0.3);
	}
	return clamp(rez, 0.0, 1.0);
}

float getsat(vec3 c)
{
    float mi = min(min(c.x, c.y), c.z);
    float ma = max(max(c.x, c.y), c.z);
    return (ma - mi)/(ma+ 1e-7);
}

//from my "Will it blend" shader (https://www.shadertoy.com/view/lsdGzN)
vec3 iLerp(in vec3 a, in vec3 b, in float x)
{
    vec3 ic = mix(a, b, x) + vec3(1e-6,0.,0.);
    float sd = abs(getsat(ic) - mix(getsat(a), getsat(b), x));
    vec3 dir = normalize(vec3(2.*ic.x - ic.y - ic.z, 2.*ic.y - ic.x - ic.z, 2.*ic.z - ic.y - ic.x));
    float lgt = dot(vec3(1.0), ic);
    float ff = dot(dir, normalize(ic));
    ic += 1.5*dir*sd*ff*lgt;
    return clamp(ic,0.,1.);
}

vec3 makeShader2(){
    vec2 q = gl_FragCoord.xy/resolution.xy;
    vec2 p = (gl_FragCoord.xy - 0.5*resolution.xy)/resolution.y;
    //bsMo = (iMouse.xy - 0.5*iResolution.xy)/iResolution.y;

    float time_m = time*3.;
    vec3 ro = vec3(0,0,time_m);

    ro += vec3(sin(time)*0.5,sin(time*1.)*0.,0);

    float dspAmp = .85;
    ro.xy += disp(ro.z)*dspAmp;
    float tgtDst = 3.5;

    vec3 target = normalize(ro - vec3(disp(time + tgtDst)*dspAmp, time + tgtDst));
    ro.x -= bsMo.x*2.;
    vec3 rightdir = normalize(cross(target, vec3(0,1,0)));
    vec3 updir = normalize(cross(rightdir, target));
    rightdir = normalize(cross(updir, target));
	vec3 rd=normalize((p.x*rightdir + p.y*updir)*1. - target);
    rd.xy *= rot(-disp(time_m + 3.5).x*0.2); //+ bsMo.x
    prm1 = smoothstep(-0.4, 0.4,sin(time*0.3));
	vec4 scn = render(ro, rd, time_m);

    vec3 col = scn.rgb;
    col = iLerp(col.bgr, col.rgb, clamp(1.-prm1,0.05,1.));

    col = pow(col, vec3(.55,0.65,0.6))*vec3(1.,.97,.9);

    col *= pow( 16.0*q.x*q.y*(1.0-q.x)*(1.0-q.y), 0.12)*0.7+0.3; //Vign
    return col;
}

vec3 makeShader3(){
    vec3 c;
	float l,z=time;
	for(int i=0;i<3;i++) {
		vec2 uv,p=gl_FragCoord.xy/resolution;
		uv=p;
		p-=.5;
		p.x*=resolution.x/resolution.y;
		z+=.07;
		l=length(p);
		uv+=p/l*(sin(z)+1.)*abs(sin(l*9.-z*2.));
		c[i]=.01/length(abs(mod(uv,1.)-.5));
	}
 return vec3(c/l);
}


void main()
{

    vec3 color = makeShader();
    gl_FragColor = vec4(color, time);
}
"""

"""float ratio = resolution.y/resolution.x;
    vec4 fake_FragCoord = gl_FragCoord;
    fake_FragCoord.y *= ratio;
    vec2 position = ( fake_FragCoord.xy / resolution.xy )-vec2(0.5,0.5*ratio);
    vec3 p = position.xyx*FIELD;
    vec3 color = computeColor(wolfFaceEQ(p+2.5,time));"""

VERTEX_SOURCE = """
#version 400
attribute vec4 position;
varying vec3 v_color;
void main()
{
    gl_Position = position;
    v_color = vec3(position.xyz);
}
"""

class ShaderWallpaper(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shaderContent = Gtk.GLArea()

        self.shaderContent

        self.shaderContent.connect("realize", self.on_realize)
        self.shaderContent.connect("render", self.on_render)
        self.shaderContent.set_has_depth_buffer(False)
        self.shaderContent.set_has_stencil_buffer(False)

        self.time = float(0.0)
        self.mod = 0.01
        self.vertices = [
            1.0,  1.0, 0.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 1.0,
            -1.0,  -1.0, 0.0, 1.0,
            1.0, -1.0, 0.0, 1.0,
            1.0,  1.0, 0.0, 1.0,]
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.set_startup_id('Oboi')
        self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_accept_focus(True)
        self.stick()
        self.set_resizable(False)
        self.set_keep_below(True)
        self.set_decorated(False)


        self.drag_dest_set(Gtk.DestDefaults.MOTION |
                           Gtk.DestDefaults.DROP, None, Gdk.DragAction.MOVE)

        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK |
                        Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.SMOOTH_SCROLL_MASK)

        self.add(self.shaderContent)
        self.show_all()



    def on_realize(self, area):
        # We need to make the context current if we want to
        # call GL API
        area.make_current()
        context = area.get_context()
        if (area.get_error() != None):
          return

        fragment_shader = shaders.compileShader(FRAGMENT_SOURCE,
                                                GL_FRAGMENT_SHADER)
        vertex_shader = shaders.compileShader(VERTEX_SOURCE,
                                              GL_VERTEX_SHADER)
        self.shaderContent.shader_prog = shaders.compileProgram(fragment_shader,
                                                           vertex_shader)
        glLinkProgram(self.shaderContent.shader_prog)
        self.vertex_array_object = glGenVertexArrays(1)
        glBindVertexArray( self.vertex_array_object )
        # Generate buffers to hold our vertices
        self.vertex_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer)


        self.position = glGetAttribLocation(self.shaderContent.shader_prog,
                                              'position')
        self.time_l = glGetUniformLocation(self.shaderContent.shader_prog,
                                         'time')
        print(self.time_l)
        # glBindAttribLocation(self.shaderContent.shader_prog, self.time, 'time')
        glEnableVertexAttribArray(self.position)
        glVertexAttribPointer(index=self.position, size=4, type=GL_FLOAT,
                              normalized=False, stride=0, pointer=ctypes.c_void_p(0))
        glBufferData(GL_ARRAY_BUFFER, 192, self.vertices, GL_STATIC_DRAW)
        glBindVertexArray(0)
        glDisableVertexAttribArray(self.position)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        self.on_render(self.shaderContent)

        return True

    def on_render(self, area, *args):
        area.attach_buffers()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(self.shaderContent.shader_prog)
        self.timer()
        glUniform1f(self.time_l, self.time)
        glBindVertexArray(self.vertex_array_object)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray( 0 )

        glUseProgram(0)
        glFlush()
        self.shaderContent.queue_render()
        return True

    def set_actors_size(self, size:tuple):
        self.width = size[0]
        self.height = size[1]

    def timer(self):
        if self.time > 100.0 or self.time == 0.0:
            self.mod *= -1
        self.time += self.mod
        # print(self.time)
        return self.time

    def display(self):
        pass

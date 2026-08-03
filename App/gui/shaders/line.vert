#version 330 core

layout(location = 0) in vec2 in_position;
layout(location = 1) in vec3 in_color;

uniform vec2 camera_position;
uniform float camera_zoom;
uniform vec2 screen_size;

out vec3 frag_color;

void main()
{
    vec2 pos = (in_position - camera_position) * camera_zoom;
    pos /= screen_size * 0.5;

    gl_Position = vec4(pos, 0.0, 1.0);

    frag_color = in_color;
}
#version 330 core

layout(location = 0) in vec2 in_vertex;

layout(location = 1) in vec2 instance_position;
layout(location = 2) in float instance_radius;
layout(location = 3) in float instance_angle;
layout(location = 4) in vec3 instance_color;

uniform vec2 camera_position;
uniform float camera_zoom;
uniform vec2 screen_size;

out vec3 frag_color;

void main()
{
    vec2 p = in_vertex;

    float c = cos(instance_angle);
    float s = sin(instance_angle);

    p = vec2(
        p.x * c - p.y * s,
        p.x * s + p.y * c
    );

    p *= instance_radius;
    p += instance_position;

    p -= camera_position;
    p *= camera_zoom;
    p /= screen_size * 0.5;

    gl_Position = vec4(p, 0.0, 1.0);

    frag_color = instance_color;
}
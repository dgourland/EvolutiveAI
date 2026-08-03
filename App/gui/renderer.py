"""
App/gui/renderer.py

Permet la gestion de l'interface grafique de l'application
"""

import math, pygame, ctypes
from App.vars import *
from .colors import *

"""
App/gui/renderer.py

Renderer OpenGL GPU.

Responsabilités :
- afficher le World
- envoyer les buffers au GPU
- gérer shaders et buffers

Ne modifie jamais World.
"""

import numpy as np

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from App.gui.camera import Camera


class Renderer:

    def __init__(
        self,
        camera,
        max_objects=10000,
        max_rays=1000,
        
    ):

        self.camera = camera
        self.max_objects = max_objects
        self.max_rays = max_rays
        self.instance_data = np.zeros(
            (
                max_objects,
                7
            ),
            dtype=np.float32
        )


        # -------------------------------------------------
        # Paramètres OpenGL
        # -------------------------------------------------

        glEnable(GL_BLEND)

        glBlendFunc(
            GL_SRC_ALPHA,
            GL_ONE_MINUS_SRC_ALPHA
        )


        glDisable(
            GL_DEPTH_TEST
        )

        
        # -------------------------------------------------
        # Shaders
        # -------------------------------------------------

        self.object_shader = self.create_shader_program(
            "./App/gui/shaders/object.vert",
            "./App/gui/shaders/object.frag"
        )


        self.line_shader = self.create_shader_program(
            "./App/gui/shaders/line.vert",
            "./App/gui/shaders/line.frag"
        )


        # -------------------------------------------------
        # Géométrie d'un cercle unité
        #
        # Le GPU transforme ce cercle pour chaque objet
        # -------------------------------------------------

        self.circle_vertices = self.create_circle(
            segments=32
        )


        self.circle_vao = glGenVertexArrays(1)

        self.circle_vbo = glGenBuffers(1)


        glBindVertexArray(
            self.circle_vao
        )


        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.circle_vbo
        )


        glBufferData(
            GL_ARRAY_BUFFER,
            self.circle_vertices.nbytes,
            self.circle_vertices,
            GL_STATIC_DRAW
        )


        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            GL_FALSE,
            0,
            None
        )


        glBindVertexArray(0)



        # -------------------------------------------------
        # Buffer d'instances objets
        #
        # x
        # y
        # radius
        # angle
        # type
        # -------------------------------------------------

        

        self.instance_vbo = glGenBuffers(1)


        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.instance_vbo
        )


        glBufferData(
            GL_ARRAY_BUFFER,
            self.instance_data.nbytes,
            None,
            GL_DYNAMIC_DRAW
        )


        # -------------------------------------------------
        # VAO objets instanciés
        # -------------------------------------------------

        glBindVertexArray(
            self.circle_vao
        )


        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.instance_vbo
        )


        stride = 7 * np.dtype(np.float32).itemsize


        # position objet

        glEnableVertexAttribArray(1)

        glVertexAttribPointer(
            1,
            2,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(0)
        )


        glVertexAttribDivisor(
            1,
            1
        )


        # radius

        glEnableVertexAttribArray(2)

        glVertexAttribPointer(
            2,
            1,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(8)
        )


        glVertexAttribDivisor(
            2,
            1
        )


        # angle

        glEnableVertexAttribArray(3)

        glVertexAttribPointer(
            3,
            1,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(12)
        )


        glVertexAttribDivisor(
            3,
            1
        )


        # type

        glEnableVertexAttribArray(4)

        glVertexAttribPointer(
            4,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(16)
        )


        glVertexAttribDivisor(
            4,
            1
        )


        glBindVertexArray(0)



        # -------------------------------------------------
        # Buffer lignes (rayons capteurs)
        # -------------------------------------------------

        print("A", glGetString(GL_VERSION))

        self.circle_vao = glGenVertexArrays(1)

        print("B", glGetString(GL_VERSION))

        self.circle_vbo = glGenBuffers(1)

        print("C", glGetString(GL_VERSION))

        
        glBindVertexArray(
            self.ray_vao
        )


        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.ray_vbo
        )


        glBufferData(
            GL_ARRAY_BUFFER,
            max_rays * 2 * 2 * 4,
            None,
            GL_DYNAMIC_DRAW
        )


        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            GL_FALSE,
            0,
            None
        )


        glBindVertexArray(0)
        print(glGetString(GL_VERSION).decode())
        print(glGetString(GL_SHADING_LANGUAGE_VERSION).decode())


    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def create_circle(self, segments=32):

        vertices = [
            [0.0,0.0]
        ]

        for i in range(segments+1):

            angle = (
                2*np.pi*i/segments
            )

            vertices.append(
                [
                    np.cos(angle),
                    np.sin(angle)
                ]
            )

        return np.array(
            vertices,
            dtype=np.float32
        )

    def create_shader_program(self, vertex_path, fragment_path):
        
        with open(vertex_path, "r") as f:
            vertex_src = f.read()

        with open(fragment_path, "r") as f:
            fragment_src = f.read()


        print("Compiling vertex shader:", vertex_path)

        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_src)
        glCompileShader(vertex_shader)

        status = glGetShaderiv(
            vertex_shader,
            GL_COMPILE_STATUS
        )

        if not status:
            print(
                glGetShaderInfoLog(vertex_shader)
            )
            raise RuntimeError("Vertex shader compilation failed")


        print("Compiling fragment shader:", fragment_path)

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_src)
        glCompileShader(fragment_shader)

        status = glGetShaderiv(
            fragment_shader,
            GL_COMPILE_STATUS
        )

        if not status:
            print(
                glGetShaderInfoLog(fragment_shader)
            )
            raise RuntimeError("Fragment shader compilation failed")


        print("Linking program")

        program = glCreateProgram()

        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        print("PROGRAM:")
        print(vertex_path)
        print(fragment_path)
        glLinkProgram(program)

        status = glGetProgramiv(
            program,
            GL_LINK_STATUS
        )

        log = glGetProgramInfoLog(program)

        if isinstance(log, bytes):
            log = log.decode()

        print("LINK STATUS:", status)
        print("LINK LOG:")
        print(log)

        if not status:
            raise RuntimeError("Shader link failed")


        print("Shader OK")

        return program
        
    def draw(self, world):

        glClearColor(
            0.31,
            0.31,
            0.31,
            1.0
        )

        glClear(
            GL_COLOR_BUFFER_BIT
        )


        count = self.upload_objects(world)


        if count == 0:
            return


        glUseProgram(self.object_shader)

        self.update_camera_uniform(
            self.object_shader
        )


        glBindVertexArray(
            self.circle_vao
        )


        glDrawArraysInstanced(
            GL_TRIANGLE_FAN,
            0,
            len(self.circle_vertices),
            count
        )


        glBindVertexArray(0)

    def upload_objects(self, world):

        count = world.valid_objects

        if count == 0:
            return 0


        self.instance_data[:count, 0] = world.object_x[:count]
        self.instance_data[:count, 1] = world.object_y[:count]
        self.instance_data[:count, 2] = world.object_radius[:count]
        self.instance_data[:count, 3] = world.object_angle[:count]
        self.instance_data[:count,4:7] = world.object_color[:count]
        
        
        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.instance_vbo
        )

        glBufferSubData(
            GL_ARRAY_BUFFER,
            0,
            self.instance_data[:count]
        )

        return count
    def update_camera_uniform(self, shader):

        loc = glGetUniformLocation(
            shader,
            "camera_position"
        )

        glUniform2f(
            loc,
            self.camera.x,
            self.camera.y
        )


        loc = glGetUniformLocation(
            shader,
            "camera_zoom"
        )

        glUniform1f(
            loc,
            self.camera.zoom
        )


        loc = glGetUniformLocation(
            shader,
            "screen_size"
        )

        glUniform2f(
            loc,
            self.camera.width,
            self.camera.height
        )
    def draw_sensor_rays(self, world):

        rays = world.spec_rays_vectors

        count = rays.shape[0]

        if count == 0:
            return


        # -------------------------------------------------
        # Conversion vers le format GPU
        #
        # Deux sommets par rayon :
        # (x1,y1,r,g,b)
        # (x2,y2,r,g,b)
        # -------------------------------------------------

        vertices = np.empty(
            (count * 2, 5),
            dtype=np.float32
        )

        vertices[0::2, 0] = rays[:, 0]
        vertices[0::2, 1] = rays[:, 1]
        vertices[0::2, 2:] = rays[:, 4:7]

        vertices[1::2, 0] = rays[:, 2]
        vertices[1::2, 1] = rays[:, 3]
        vertices[1::2, 2:] = rays[:, 4:7]


        # -------------------------------------------------
        # Upload GPU
        # -------------------------------------------------

        glUseProgram(self.line_shader)

        self.update_camera_uniform(
            self.line_shader
        )

        glBindVertexArray(
            self.ray_vao
        )

        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.ray_vbo
        )

        glBufferData(
            GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices,
            GL_DYNAMIC_DRAW
        )


        stride = 5 * np.dtype(np.float32).itemsize


        # Position

        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(0)
        )


        # Couleur

        glEnableVertexAttribArray(1)

        glVertexAttribPointer(
            1,
            3,
            GL_FLOAT,
            GL_FALSE,
            stride,
            ctypes.c_void_p(8)
        )


        glDrawArrays(
            GL_LINES,
            0,
            count * 2
        )

        glBindVertexArray(0)
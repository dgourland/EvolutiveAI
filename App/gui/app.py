"""
App/gui/app.py

SimulationApp est la classe principale de l'application
"""
import pygame
from App.simulation import Simulation
from .camera import Camera
import time, os
import numpy as np
os.environ["PYOPENGL_PLATFORM"] = "glx"
from OpenGL import platform
from OpenGL.GL import *
import pygame._sdl2.video as sdl2
print("Var PyOpenGL Platform : ",os.environ.get("PYOPENGL_PLATFORM"))
print("Pygame SDL Version : ",pygame.get_sdl_version())
import traceback
class SimulationApp:

    def __init__(self, 
            generation_steps=3000,
            population_size=100,
            food_amount=200,
            world_width=1200,
            world_height=800,
            starting_dna=None,
            starting_mutation_rate=0.02,
            starting_mutation_strength=0.02,
            respawn_food_size=5,
            respawn_food_rate=10,
            fov=90,
            max_distance=200,
            rays=10,
            rays_points=5,
            GUI=True
            ):

        self.GUI=GUI
        self.sim = Simulation(
            generation_steps=generation_steps,
            population_size=population_size,
            food_amount=food_amount,
            world_width=world_width,
            world_height=world_height, 
            starting_dna=starting_dna,
            starting_mutation_rate=starting_mutation_rate,
            starting_mutation_strength=starting_mutation_strength,
            max_distance=max_distance,
            fov=fov,
            rays=rays,
            rays_points=rays_points
            
        )
        self.respawn_food_size=respawn_food_size
        self.respawn_food_rate=respawn_food_rate
        self.world = self.sim.world
        
        self.dt=0
        self.fps=0
        self.acceleration=1

        self.clock = pygame.time.Clock()

        

        self.running = True

        self.paused = False
        # Performance monitoring
        self.spectator_mode=False
        self.simulation_ms = 0
        self.render_ms = 0

        self.update_counter = 0
        self.updates_per_second = 0
        self.spectator_index=-1

        self.last_second = time.perf_counter()
        self.stats = {
            "fps": 0,
            "updates": 0,
            "population": 0,
            "food": 0,
            "render_ms": 0
        }
        
        self.sim_updates = 0
        self.last_time = time.time()
        self.updates_per_second = 0
        self.moy_render_ms=0

        for file in os.listdir("./logs"):
            os.remove("./logs/"+file)

    def run(self):
        if self.GUI:

            pygame.init()

            pygame.display.gl_set_attribute(
                pygame.GL_CONTEXT_MAJOR_VERSION, 3
            )
            pygame.display.gl_set_attribute(
                pygame.GL_CONTEXT_MINOR_VERSION, 3
            )
            pygame.display.gl_set_attribute(
                pygame.GL_CONTEXT_PROFILE_MASK,
                pygame.GL_CONTEXT_PROFILE_CORE
            )
            self.screen = pygame.display.set_mode(
                (self.world.width, self.world.height),
                pygame.OPENGL | pygame.DOUBLEBUF,
                vsync=0
            )
            print("SDL Window :", sdl2.Window.from_display_module())
            print(platform)
            print(type(platform))
            print(platform.PLATFORM)
            print("Context:", platform.GetCurrentContext())
            print("Version:", glGetString(GL_VERSION))
            pygame.display.set_caption(
                "Evolution Simulation"
            )
            print(glGetString(GL_VERSION).decode())
            print(glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
            glViewport(0, 0, self.world.width, self.world.height)
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            self.camera = Camera(self.world.width, self.world.height)
            print("GL VERSION before Renderer:",
                glGetString(GL_VERSION))
            print("GL Context before Renderer :,",
                platform.GetCurrentContext())
            print("Vendor  :", glGetString(GL_VENDOR).decode())
            print("Renderer:", glGetString(GL_RENDERER).decode())
            print("GL error:",
                glGetError())
            self.renderer = Renderer(
                camera=self.camera,
                max_rays=self.sim.world.MAX_RAYS
            )
            self.ui = UI(self.world.width, self.world.height)
        while self.running:
            single_app_iteration=time.perf_counter()


            self.handle_events()
            


            # -------------------------
            # Simulation timing
            # -------------------------

            start = time.perf_counter()
            used_time_start = time.perf_counter()

            if not self.paused:
                if self.world.time%(self.respawn_food_rate*60)==0:
                    self.world.spawn_food(self.respawn_food_size)
                    
                self.sim.update()

                self.update_counter += 1
                if self.sim.generation_finished():

                    self.sim.world.logger.save(self.sim.generation)

                    self.sim.evolve()
                    self.sim.generation+=1

                

            end = time.perf_counter()

            if self.world.time%60==0:
                self.simulation_ms = (
                    end - start
                ) * 1000



            # -------------------------
            # Rendering timing
            # -------------------------

            start = time.perf_counter()

            gui_renderer_time=0
            if self.GUI:
                start_gui = time.perf_counter()
                if self.spectator_mode and self.world.creatures:

                    self.spectator_index %= len(self.world.creatures)

                    creature = self.world.creatures[
                        self.spectator_index
                    ]

                    self.world.spectator = creature.object_id

                    self.camera.follow(
                        self.world.spectator,
                        self.world
                    )

                    self.camera.zoom = 2

                else:

                    self.world.spectator = -1
                    self.camera.zoom = 1
                draw_time = time.perf_counter()
                self.renderer.draw(
                    self.world
                )
                gui_draw_time=time.perf_counter()-draw_time
                rays_draw=time.perf_counter()
                if self.spectator_mode:
                    self.renderer.draw_sensor_rays(self.world)
                rays_draw_time=time.perf_counter()-rays_draw
                self.ui.draw(
                    self
                )
                

                end = time.perf_counter()


                self.render_ms = (
                    end - start
                ) * 1000

                if self.moy_render_ms == 0:
                    self.moy_render_ms=self.render_ms
                else:
                    self.moy_render_ms = (self.moy_render_ms+self.render_ms)/2
                flip_time=time.perf_counter()
                pygame.display.flip()
                flip_time_delta = time.perf_counter()-flip_time
                gui_renderer_time = time.perf_counter()-start_gui
            
                



            # -------------------------
            # FPS
            # -------------------------
            used_time = time.perf_counter()-used_time_start
            if self.GUI:
                self.clock.tick(60*self.acceleration)

            self.fps = self.clock.get_fps()



            # -------------------------
            # UPS counter
            # -------------------------

            now = time.perf_counter()


            if now - self.last_second >= 1:


                self.updates_per_second = (
                    self.update_counter
                )


                self.update_counter = 0

                self.last_second = now
            if self.world.time%60*2==0:
                app_iteration = time.perf_counter()-single_app_iteration
                print("GUI renderer time : ", gui_renderer_time*1000, "ms")
                print("\tGUI draw : ", gui_draw_time*1000, "ms")
                print("\tGUI rays draw : ", rays_draw_time*1000, "ms")
                print("\tPygame flip : ", flip_time_delta*1000, "ms")
                print("Free time remaining: ", (app_iteration-used_time)*1000, "ms")
                print("Total app time per ticks: ", (app_iteration)*1000, "ms")
           

                

            
                
        if self.GUI:
            pygame.quit()

    def handle_events(self):
        if not self.GUI:
            return
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_SPACE:

                    self.paused = not self.paused

                elif event.key == pygame.K_e:

                    self.spectator_mode = not self.spectator_mode

                    if self.spectator_index >= len(self.world.creatures):
                        self.spectator_index = 0

                    
                elif event.key == pygame.K_z:
                    self.acceleration+=1

                elif event.key == pygame.K_s:
                    if (self.acceleration-1)>=1:
                        self.acceleration-=1
                        
                elif self.spectator_mode:

                    if event.key == pygame.K_RIGHT :

                        self.spectator_index = (self.spectator_index+1)%len(self.world.creatures)

                        

                    elif event.key == pygame.K_LEFT:

                        self.spectator_index = (self.spectator_index-1)%len(self.world.creatures)




class Renderer:

    def __init__(
        self,
        camera,
        max_objects=10000,
        max_rays=1000
        
    ):
        
        try :

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
            print("Circles : OK")

            glEnableVertexAttribArray(0)
            print("124")
            glVertexAttribPointer(
                0,
                2,
                GL_FLOAT,
                GL_FALSE,
                0,
                ctypes.c_void_p(0)
            )
            print("133")

            glBindVertexArray(0)
            print("136") 


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
            print("152")

            glBindBuffer(
                GL_ARRAY_BUFFER,
                self.instance_vbo
            )
            print("158")

            glBufferData(
                GL_ARRAY_BUFFER,
                self.instance_data.nbytes,
                None,
                GL_DYNAMIC_DRAW
            )
            print(166)

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

            print("Instance : OK")
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
            print("Stride : OK")
            self.ray_vao=glGenVertexArrays(1)
            self.ray_vbo=glGenBuffers(1)

            
            glBindVertexArray(
                self.ray_vao
            )


            glBindBuffer(
                GL_ARRAY_BUFFER,
                self.ray_vbo
            )

            glBufferData(
                GL_ARRAY_BUFFER,
                max_rays * 2 * 5 * 4,
                None,
                GL_DYNAMIC_DRAW
            )
            stride = 5 * np.dtype(np.float32).itemsize

            


            glEnableVertexAttribArray(0)
            glVertexAttribPointer(
                0,
                2,
                GL_FLOAT,
                GL_FALSE,
                stride,
                ctypes.c_void_p(0)
            )

            glEnableVertexAttribArray(1)
            glVertexAttribPointer(
                1,
                3,
                GL_FLOAT,
                GL_FALSE,
                stride,
                ctypes.c_void_p(8)
            )

            print("Rays : OK")
            glBindVertexArray(0)
            print(glGetString(GL_VERSION).decode())
            print(glGetString(GL_SHADING_LANGUAGE_VERSION).decode())
            self.vertices = np.empty(
                        (max_rays*2, 5),
                        dtype=np.float32
                    )
            glClearColor(
                        0.31,
                        0.31,
                        0.31,
                        1.0
                    )
        except Exception as e:
            self.check_gl("Error : ", e)
            exit(1)

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

        return ShaderProgram(program)
        
    def draw(self, world):

        

        glClear(
            GL_COLOR_BUFFER_BIT
        )


        count = self.upload_objects(world)


        if count == 0:
            return


        glUseProgram(self.object_shader.id)

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

        # self.instance_data = world.object_data


        self.instance_data[:count] = world.object_data[:count]
        
        
        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.instance_vbo
        )

        glBufferSubData(
            GL_ARRAY_BUFFER,
            0,
            self.instance_data[:count].nbytes,
            self.instance_data[:count]
        )

        return count
    def update_camera_uniform(self, shader):
        glUniform2f(
            shader.uniforms["camera_position"],
            self.camera.x,
            self.camera.y
        )


        glUniform1f(
            shader.uniforms["camera_zoom"],
            self.camera.zoom
        )


        glUniform2f(
            shader.uniforms["screen_size"],
            self.camera.width,
            self.camera.height
        )

    def draw_sensor_rays(self, world):

        rays = world.spec_rays_vectors

        count = world.valid_rays

        if count == 0:
            return


        # Création des sommets
        self.vertices[0::2, 0] = rays[:, 0]
        self.vertices[0::2, 1] = rays[:, 1]
        self.vertices[0::2, 2:] = rays[:, 4:7]

        self.vertices[1::2, 0] = rays[:, 2]
        self.vertices[1::2, 1] = rays[:, 3]
        self.vertices[1::2, 2:] = rays[:, 4:7]


        # Upload GPU
        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.ray_vbo
        )

        glBufferSubData(
            GL_ARRAY_BUFFER,
            0,
            self.vertices.nbytes,
            self.vertices
        )


        glUseProgram(
            self.line_shader.id
        )

        self.update_camera_uniform(
            self.line_shader
        )


        glBindVertexArray(
            self.ray_vao
        )

        glDrawArrays(
            GL_LINES,
            0,
            count * 2
        )


        glBindVertexArray(0)

    def check_gl(self, msg:str, e:Exception):
        err = glGetError()
        if err != GL_NO_ERROR:
            print(msg, hex(err))
        else:
            traceback.print_exc()
            print(e)
class ShaderProgram:

    def __init__(self, program):
        self.id = program

        self.uniforms = {}

        for name in [
            "camera_position",
            "camera_zoom",
            "screen_size"
        ]:
            self.uniforms[name] = glGetUniformLocation(
                program,
                name
            )


class UI:


    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.font = pygame.font.SysFont(
            "Arial",
            20
        )

        # pygame surface used for text rendering
        self.surface = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )


        # OpenGL texture

        self.texture = glGenTextures(1)

        glBindTexture(
            GL_TEXTURE_2D,
            self.texture
        )

        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_MIN_FILTER,
            GL_LINEAR
        )

        glTexParameteri(
            GL_TEXTURE_2D,
            GL_TEXTURE_MAG_FILTER,
            GL_LINEAR
        )


        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            None
        )


        # shader

        self.shader = self.create_shader()


        # fullscreen quad

        vertices = np.array([
            -1,  1, 0, 0,
            -1, -1, 0, 1,
             1, -1, 1, 1,

            -1,  1, 0, 0,
             1, -1, 1, 1,
             1,  1, 1, 0
        ], dtype=np.float32)


        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)


        glBindVertexArray(self.vao)

        glBindBuffer(
            GL_ARRAY_BUFFER,
            self.vbo
        )

        glBufferData(
            GL_ARRAY_BUFFER,
            vertices.nbytes,
            vertices,
            GL_STATIC_DRAW
        )


        stride = 4 * 4

        self.last_ui_update=0
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(
            0,
            2,
            GL_FLOAT,
            False,
            stride,
            ctypes.c_void_p(0)
        )


        glEnableVertexAttribArray(1)

        glVertexAttribPointer(
            1,
            2,
            GL_FLOAT,
            False,
            stride,
            ctypes.c_void_p(8)
        )


        glBindVertexArray(0)



    def create_shader(self):

        vertex = """
        #version 330

        layout(location=0) in vec2 pos;
        layout(location=1) in vec2 uv;

        out vec2 TexCoord;

        void main()
        {
            TexCoord = uv;
            gl_Position = vec4(pos,0,1);
        }
        """


        fragment = """
        #version 330

        in vec2 TexCoord;

        uniform sampler2D tex;

        out vec4 color;

        void main()
        {
            color = texture(tex, TexCoord);
        }
        """


        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, vertex)
        glCompileShader(vs)


        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, fragment)
        glCompileShader(fs)


        program = glCreateProgram()

        glAttachShader(program,vs)
        glAttachShader(program,fs)

        glLinkProgram(program)


        return program



    def draw(self, app):
        test=time.perf_counter()
        if (test-self.last_ui_update)>0.2:
            self.last_ui_update=test
            self.surface.fill((0,0,0,0))

            data = [
                f"FPS: {app.fps:.1f}",
                f"UPS: {app.updates_per_second}",
                f"Simulation: {app.simulation_ms:.3f} ms",
                f"Render: {app.render_ms:.3f} ms",
                f"Creatures: {len(app.world.creatures)}",
                f"Food: {len(app.world.foods)}",
                f"Generation: {app.sim.generation}",
                f"Time: {app.world.time}",
                f"Speed: x{app.acceleration}"
            ]

            y=10

            for line in data:

                txt=self.font.render(
                    line,
                    True,
                    (255,255,255)
                )

                self.surface.blit(txt,(10,y))
                y+=25


            pixels=pygame.image.tostring(
                self.surface,
                "RGBA",
                False
            )


            glBindTexture(
                GL_TEXTURE_2D,
                self.texture
            )
            glTexSubImage2D(
                GL_TEXTURE_2D,
                0,                      # mip level
                0,                      # xoffset
                0,                      # yoffset
                self.width,
                self.height,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                pixels
            )

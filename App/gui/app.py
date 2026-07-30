"""
App/gui/app.py

SimulationApp est la classe principale de l'application
"""
import pygame
from App.simulation import Simulation
from .camera import Camera
from .renderer import Renderer
from .ui import UI
import time, os

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
       
        
        self.spectator_mode = False
        self.spectator_index = 0
        self.clock = pygame.time.Clock()

        

        self.running = True

        self.paused = False
        # Performance monitoring

        self.simulation_ms = 0
        self.render_ms = 0

        self.update_counter = 0
        self.updates_per_second = 0

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
            self.screen = pygame.display.set_mode(
                (self.world.width, self.world.height)
            )
            pygame.display.set_caption("Evolution Simulation")
            self.camera = Camera()
            
            self.renderer = Renderer(
                self.screen,
                self.camera
            )
            self.ui = UI()
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

            spectator = None
            if self.GUI:
                if self.spectator_mode and self.world.creatures:

                    self.spectator_index %= len(self.world.creatures)

                    spectator = self.world.creatures[self.spectator_index]

                    self.camera.follow(
                        spectator,
                        self.world.width,
                        self.world.height
                    )
                    self.camera.zoom=2
                else:
                    self.camera.zoom=1

                self.renderer.draw(
                    self.world,
                    spectator
                )
                self.ui.draw(self.screen,self)


                end = time.perf_counter()


                self.render_ms = (
                    end - start
                ) * 1000

                if self.moy_render_ms == 0:
                    self.moy_render_ms=self.render_ms
                else:
                    self.moy_render_ms = (self.moy_render_ms+self.render_ms)/2

                pygame.display.flip()



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

                    if not self.spectator_mode:
                        self.camera.x = 0
                        self.camera.y = 0
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
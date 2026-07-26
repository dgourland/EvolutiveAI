import pygame
from App.simulation import Simulation
from .camera import Camera
from .renderer import Renderer
from .ui import UI
import time
class SimulationApp:

    def __init__(self, 
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
            rays_points=5
            ):

        pygame.init()
        self.sim = Simulation(
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

        self.screen = pygame.display.set_mode(
            (self.world.width, self.world.height)
        )
        self.dt=0
        self.fps=0
       
        pygame.display.set_caption("Evolution Simulation")
        self.spectator_mode = False
        self.spectator_index = 0
        self.clock = pygame.time.Clock()

        self.camera = Camera()

        self.renderer = Renderer(
            self.screen,
            self.camera
        )

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
        self.ui = UI()
        self.sim_updates = 0
        self.last_time = time.time()
        self.updates_per_second = 0
        self.moy_render_ms=0

    def run(self):
        
        while self.running:


            self.handle_events()
            


            # -------------------------
            # Simulation timing
            # -------------------------

            start = time.perf_counter()


            if not self.paused:

                self.sim.update()

                self.update_counter += 1
                if self.sim.generation_finished():

                    self.sim.world.logger.save(self.sim.generation)

                    self.sim.evolve()
                    self.sim.generation+=1
                if self.update_counter%(self.respawn_food_rate*60)==0:
                    self.world.spawn_food(self.respawn_food_size)

            end = time.perf_counter()


            self.simulation_ms = (
                end - start
            ) * 1000



            # -------------------------
            # Rendering timing
            # -------------------------

            start = time.perf_counter()

            spectator = None

            if self.spectator_mode and self.world.creatures:

                self.spectator_index %= len(self.world.creatures)

                spectator = self.world.creatures[self.spectator_index]

                self.camera.follow(
                    spectator,
                    self.world.width,
                    self.world.height
                )

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

            self.clock.tick(60)

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
            if self.update_counter % 60 == 0:

                print(
    f"""
    SIM:
    {self.simulation_ms:.2f} ms

    RENDER:
    {self.moy_render_ms:.2f} ms
    """
                )

            
                

        pygame.quit()

    def handle_events(self):

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

                elif self.spectator_mode:

                    if event.key == pygame.K_RIGHT :

                        self.spectator_index = (self.spectator_index+1)%len(self.world.creatures)

                        

                    elif event.key == pygame.K_LEFT:

                        self.spectator_index = (self.spectator_index-1)%len(self.world.creatures)
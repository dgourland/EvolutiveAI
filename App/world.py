"""
App/world.py

Gestion du monde de simulation.

Le monde contient :

- créatures
- nourriture
- grille spatiale

Il orchestre les interactions physiques.
"""

from App.death_record import DeathRecord
from App.physics.spatial_grid import SpatialGrid
from App.entities.food import Food
from App.utils.logger import SimulationLogger
import time, random
from App.sensors.sensors import SensorSystem
from App.entities.creature import Creature
from App.vars import *
import numpy as np

class World:


    def __init__(
        self,
        width=1200,
        height=800,
        generation=0
    ):

        self.logger = SimulationLogger()

        self.width = width
        self.height = height

        self.generation = generation
        
        self.dead_creatures = {
            1: [],
            2: []
        }


        # ------------------------------------------------
        # Entités
        # ------------------------------------------------

        self.creatures = []

        self.deads = []

        self.foods = []


        # ------------------------------------------------
        # Object buffers for spatial/raycast system
        # ------------------------------------------------
        #
        # Index = object id used by SpatialGrid
        #
        # creatures:
        #   0 -> len(creatures)-1
        #
        # foods:
        #   len(creatures) -> end
        #

        MAX_OBJECTS = 10000

        self.object_x = np.zeros(
            MAX_OBJECTS,
            dtype=np.float32
        )

        self.object_y = np.zeros(
            MAX_OBJECTS,
            dtype=np.float32
        )

        self.object_radius = np.zeros(
            MAX_OBJECTS,
            dtype=np.float32
        )

        self.object_type = np.zeros(
            MAX_OBJECTS,
            dtype=np.int32
        )

        self.object_last_query = np.zeros(
            MAX_OBJECTS,
            dtype=np.int32
        )


        self.object_count = 0


        # ------------------------------------------------
        # Spatial hash grid
        # ------------------------------------------------

        self.spatial_grid = SpatialGrid(
            width,
            height,
            cell_size=64
        )


        self.sensor_system = None

        # object_id -> python object
        self.object_ref = []


        # ------------------------------------------------
        # Temps simulation
        # ------------------------------------------------

        self.time = 0


    # ----------------------------------------------------
    # Ajout objets
    # ----------------------------------------------------

    def add_creature(
        self,
        creature
    ):

        self.creatures.append(
            creature
        )



    def add_food(
        self,
        food
    ):

        self.foods.append(
            food
        )



    # ----------------------------------------------------
    # Création nourriture
    # ----------------------------------------------------

    def spawn_food(
        self,
        amount
    ):


        for _ in range(amount):

            food = Food(
                world_width=self.width,
                world_height=self.height
            )


            self.foods.append(
                food
            )

    def creature_dies(
            self,
            amount,
            x,
            y
        ):

            for _ in range(amount):
    
                food = Food(
                    world_width=self.width,
                    world_height=self.height
                )
                x=random.randint(-5, 5)+x
                y=random.randint(-5, 5)+y
                if (x>=self.width):
                    x=self.width-1
                if (y>=self.height):
                    y=self.height-1
                food.setPos(x, y)


                self.foods.append(
                    food
                )


    # ----------------------------------------------------
    # Reconstruction grille
    # ----------------------------------------------------

    def update_spatial_grid(self):

        self.object_ref.clear()

        self.object_count = 0

        grid = self.spatial_grid

        grid.clear()

        self.object_count = 0

        # -----------------------------
        # Creatures
        # -----------------------------

        for creature in self.creatures:

            object_id = self.object_count

            # Store the spatial id inside the creature
            creature.object_id = object_id
            self.object_ref.append(creature)

            self.object_x[object_id] = creature.x
            self.object_y[object_id] = creature.y
            self.object_radius[object_id] = creature.radius
            self.object_type[object_id] = creature.type


            self.object_last_query[object_id] = -1


            self.spatial_grid.insert(
                object_id,
                creature.x,
                creature.y,
                creature.radius
            )


            self.object_count += 1

        # -----------------------------
        # Food
        # -----------------------------

        for food in self.foods:

            obj = self.object_count
            self.object_ref.append(food)
            self.object_ref[obj] = food

            self.object_x[obj] = food.x
            self.object_y[obj] = food.y
            self.object_radius[obj] = food.radius
            self.object_type[obj] = food.type
            self.object_last_query[obj] = -1

            grid.insert(
                obj,
                food.x,
                food.y,
                food.radius
            )

            self.object_count += 1

        grid.finalize()

    def update(self):
        
        total_start = time.perf_counter()


        self.time += 1


        # -----------------------------
        # Spatial grid
        # -----------------------------

        start = time.perf_counter()

        self.update_spatial_grid()

        grid_time = (
            time.perf_counter() - start
        ) * 1000



        # -----------------------------
        # Creatures
        # -----------------------------
        

        start = time.perf_counter()
        sensor_time=0
        brain_time=0
        movement_time=0
        breeding_time=0

        for creature in self.creatures:
            sensor = time.perf_counter()
            creature.update_sensor(self)
            sensor_time+=(time.perf_counter() - sensor)*1000

            brain = time.perf_counter()
            creature.update_brain()
            brain_time+= (time.perf_counter() - brain)*1000

            moves = time.perf_counter()
            creature.update_movement()
            movement_time+= (time.perf_counter() - moves)*1000

            breeding = time.perf_counter()
            creature.update_breeding(self)
            breeding_time += (time.perf_counter() - breeding)*1000

        
        creature_time = (
            time.perf_counter() - start
        ) * 1000



        # -----------------------------
        # Food
        # -----------------------------

        start = time.perf_counter()

        self.handle_food()
        

        food_time = (
            time.perf_counter() - start
        ) * 1000



        # -----------------------------
        # Cleanup
        # -----------------------------

        start = time.perf_counter()

        self.cleanup()

        cleanup_time = (
            time.perf_counter() - start
        ) * 1000



        total_time = (
            time.perf_counter()
            -
            total_start
        ) * 1000



        if self.time % 60*2 == 0:

            print(
                f"""
    WORLD UPDATE
    ------------
    Total: {total_time:.2f} ms

    Grid:
    {grid_time:.2f} ms

    Creatures:
    {creature_time:.2f} ms

    Food:
    {food_time:.2f} ms

    Cleanup:
    {cleanup_time:.2f} ms

    Creatures::brain:
    {brain_time:.2f} ms

    Creature::breeding:
    {breeding_time:.2f} ms

    Creature::moves:
    {movement_time:.2f} ms

    Creature::sensor:
    {sensor_time:.2f} ms
    """
            )

        


    # ----------------------------------------------------
    # Nourriture
    # ----------------------------------------------------

    def handle_food(self):

        grid = self.spatial_grid

        cell_size = grid.cell_size
        grid_width = grid.grid_width
        grid_height = grid.grid_height

        object_ref = self.object_ref

        for creature in self.creatures:

            search_radius = creature.radius + 10

            min_x = max(
                0,
                int((creature.x - search_radius) // cell_size)
            )

            max_x = min(
                grid_width - 1,
                int((creature.x + search_radius) // cell_size)
            )

            min_y = max(
                0,
                int((creature.y - search_radius) // cell_size)
            )

            max_y = min(
                grid_height - 1,
                int((creature.y + search_radius) // cell_size)
            )

            # ------------------------------------------
            # Scan neighbouring cells
            # ------------------------------------------

            for cy in range(min_y, max_y + 1):

                row = cy * grid_width

                for cx in range(min_x, max_x + 1):

                    cell_id = row + cx

                    start = grid.cell_start[cell_id]
                    end = grid.cell_end[cell_id]

                    for index in range(start, end):

                        obj = object_ref[
                            grid.object_ids[index]
                        ]

                        if obj is creature:
                            continue

                        if creature.type == PREY.type:

                            if obj.type != FOOD.type:
                                continue

                        else:

                            if obj.type != PREY.type:
                                continue

                        dx = obj.x - creature.x
                        dy = obj.y - creature.y

                        limit = creature.radius + obj.radius

                        if dx * dx + dy * dy > limit * limit:
                            continue

                        creature.eat(obj)
                        obj.consume()

    # ----------------------------------------------------
    # Nettoyage
    # ----------------------------------------------------

    def cleanup(self):


        alive = []



        for creature in self.creatures:


            if creature.alive():

                alive.append(
                    creature
                )
            else:
                # self.deads.append(DeathRecord(creature, self.time))
                if creature.type==PREDATOR.type:
                    self.creature_dies(4, creature.x, creature.y)

                self.dead_creatures[creature.type].append(creature)
                


        self.creatures = alive



        self.foods = [

            f for f in self.foods

            if f.alive

        ]

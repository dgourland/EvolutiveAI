"""
world.py

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

        self.generation=generation
        self.dead_creatures = {1:[],2:[]}
        
        # ------------------------------------------------
        # Entités
        # ------------------------------------------------

        self.creatures = []

        self.deads= []

        self.foods = []


        # ------------------------------------------------
        # Spatial hash grid
        # ------------------------------------------------

        self.spatial_grid = SpatialGrid(
            cell_size=64
        )
        self.sensor_system = None



        # compteur temps

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


        objects = (

            self.creatures
            +
            self.foods

        )


        self.spatial_grid.rebuild(
            objects
        )



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

        for creature in self.creatures:
            creature.update_sensor(self)


        for creature in self.creatures:
            creature.update_brain()


        for creature in self.creatures:
            creature.update_movement()

        self.update_breeding()

        creature_time = (
            time.perf_counter() - start
        ) * 1000



        # -----------------------------
        # Food
        # -----------------------------

        start = time.perf_counter()

        self.handle_food()
        self.handle_predation()

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



        if self.time % 60 == 0:

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
    """
            )
    def update_breeding(self):
        for creature in self.creatures:
            if creature.energy>=175:
               creature.energy=50
               creature.childs+=1
               child=Creature(
                    creature.dna.mutate(
                        rate=0.02,
                        strength=0.15
                    ),
                    creature.type,
                    creature.ray_count,
                    self.width,
                    self.height
                )
               child.setPos(creature.x+random.randint(0, 5)-random.randint(0, 5), creature.y+random.randint(0, 5)-random.randint(0, 5), creature.angle+random.randint(0, 5)-random.randint(0, 5))
               self.add_creature(
                    child    
               )
        


    # ----------------------------------------------------
    # Nourriture
    # ----------------------------------------------------

    def handle_food(self):

        eaten = []

        for creature in self.creatures:
            if creature.type!=PREY.type:
                continue

            nearby = self.spatial_grid.query_radius(

                creature.x,

                creature.y,

                creature.radius + 10

            )



            for obj in nearby:


                if obj.type != FOOD.type:

                    continue



                distance = creature.distance_to(
                    obj
                )


                if (
                    distance
                    <
                    creature.radius
                    +
                    obj.radius
                ):


                    creature.eat(
                        obj
                    )


                    obj.consume()


                    eaten.append(
                        obj
                    )



        for food in eaten:


            if food in self.foods:

                self.foods.remove(
                    food
                )

    # ----------------------------------------------------
    # Nourriture
    # ----------------------------------------------------

    def handle_predation(self):


        eaten = []



        for creature in self.creatures:
            if (creature.type!=PREDATOR.type):
                continue

            nearby = self.spatial_grid.query_radius(

                creature.x,

                creature.y,

                creature.radius + 10

            )



            for obj in nearby:


                if obj.type != PREY.type:

                    continue



                distance = creature.distance_to(
                    obj
                )


                if (
                    distance
                    <
                    creature.radius
                    +
                    obj.radius
                ):


                    creature.eat(
                        obj
                    )


                    obj.consume()


                    eaten.append(
                        obj
                    )



        for food in eaten:


            if food in self.foods:

                self.foods.remove(
                    food
                )



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
                self.logger.log_death(
                    DeathRecord(creature, self.time),
                    self.time,
                    self.generation,
                    cause="energy_depleted"
                )


        self.creatures = alive



        self.foods = [

            food

            for food in self.foods

            if food.alive

        ]

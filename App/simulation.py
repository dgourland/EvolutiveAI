"""
simulation.py

Gestion de l'évolution.

Cette classe orchestre :

- générations
- sélection naturelle
- reproduction
- mutation

Elle ne gère pas :
- affichage
- physique détaillée
"""

import random

from App.world import World
from App.genetics.dna import DNA
from App.brain.neural_network import NeuralNetwork
from App.entities.creature import Creature
from App.physics.raycaster import Raycaster
from App.utils.logger import SimulationLogger
from App.sensors.sensors import SensorSystem

class Simulation:

    def __init__(
        self,
        rays=9,
        population_size=100,
        food_amount=200,
        world_width=1200,
        world_height=800,
        generation_steps=3000,
        starting_dna=None,
        starting_mutation_rate=0.02,
        starting_mutation_strength=0.15,
        fov=90,
        max_distance=200,
        rays_points=5
        
    ):

        self.population_size = population_size
        self.food_amount = food_amount

        self.logger = SimulationLogger()
        self.rays=rays

        self.starting_dna = starting_dna

        self.starting_mutation_rate = (
            starting_mutation_rate
        )

        self.starting_mutation_strength = (
            starting_mutation_strength
        )

        self.generation = 0

        self.max_steps = generation_steps
        self.current_step = 0

        self.world = World(
            world_width,
            world_height,
            self.generation
        )

        self.raycaster = Raycaster(
            self.world.spatial_grid,
            step=rays_points
        )

        self.world.sensor_system = SensorSystem(
                raycaster=self.raycaster,
                ray_count=self.rays,
                field_of_view=fov,
                max_distance=max_distance
                
            )
        self.creatures = []
        
        self.create_initial_population()

    # ----------------------------------------------------
    # Population initiale
    # ----------------------------------------------------

    def create_initial_population(self):

        input_size = (
            self.rays * 2
        )

        dna_size = NeuralNetwork.dna_size(
            input_size
        )

        self.creatures = []

        for _ in range(self.population_size):

            if self.starting_dna is not None:
                dna = DNA(DNA.random(dna_size))
                dna.loadDna(self.starting_dna)
                dna = dna.mutate(
                    rate=self.starting_mutation_rate,
                    strength=self.starting_mutation_strength
                )

            else:

                dna = DNA.random(
                    dna_size
                )


            creature = Creature(
                dna,
                self.rays,
                self.world.width,
                self.world.height
            )

            self.creatures.append(
                creature
            )

        self.world.creatures = self.creatures

        self.world.foods.clear()

        self.world.spawn_food(
            self.food_amount
        )

    # ----------------------------------------------------
    # Une frame de simulation
    # ----------------------------------------------------

    def update(self):

        self.world.update()
        
        self.current_step += 1

    # ----------------------------------------------------
    # Etat de la génération
    # ----------------------------------------------------

    def generation_finished(self):

        if self.current_step >= self.max_steps:
            return True

        if len(self.world.creatures) == 0:
            return True

        return False

    # ----------------------------------------------------
    # Fin de génération
    # ----------------------------------------------------

    def end_generation(self):

        print(f"Fin génération {self.generation}")

        self.world.logger.save(
            self.generation
        )

        self.evolve()

    # ----------------------------------------------------
    # Compatibilité avec l'ancien code
    # ----------------------------------------------------

    def run_generation(self):

        print(f"Début génération {self.generation}")

        while not self.generation_finished():
            self.update()

        self.end_generation()

    # ----------------------------------------------------
    # Sélection naturelle
    # ----------------------------------------------------

    def evolve(self):

        population = self.world.creatures

        if len(population) == 0:

            print("Extinction totale")

            self.create_initial_population()

            self.current_step = 0

            self.world.time = 0

            return

        population.sort(
            key=lambda c: c.fitness,
            reverse=True
        )

        survivors_count = max(
            2,
            int(len(population) * 0.1)
        )

        survivors = population[:survivors_count]

        print(
            f"Génération {self.generation} | "
            f"Best score : {survivors[0].score}"
        )

        from App.data import NAMELIST
        import random, os
        
        for files in os.listdir("./survivors"):
            os.remove("./survivors/"+files)

        for puppy in survivors:
            with open(f"survivors/{NAMELIST[random.randint(0, NAMELIST.__len__())]}.dna", "w") as f:
                f.write(puppy.dna.dumpDna())


        new_population = []

        while len(new_population) < self.population_size:

            parent = random.choice(
                survivors
            )

            child_dna = parent.dna.mutate(
                rate=0.03,
                strength=0.15
            )

            child = Creature(
                child_dna,
                self.rays,
                self.world.width,
                self.world.height
            )

            new_population.append(
                child
            )

        self.creatures = new_population

        self.world.creatures = self.creatures

        self.world.foods.clear()

        self.world.spawn_food(
            self.food_amount
        )

        self.generation += 1
        self.current_step = 0

        self.world.time = 0
        self.world.generation = self.generation

        print(f"Début génération {self.generation}")
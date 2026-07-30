"""
App/simulation.py

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


from App.world import World
from App.genetics.dna import DNA
from App.brain.neural_network import NeuralNetwork
from App.entities.creature import Creature
from App.physics.raycaster import Raycaster
from App.utils.logger import SimulationLogger
from App.sensors.predator_sensor import PredatorSensorSystem
from App.sensors.preys_sensor import PreySensorSystem
from App.vars import * 
from App.data import DataClass
from App.death_record import DeathRecord
import os as OS
import random
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
            self.world
        )

        self.world.sensor_system = {
            PREY.type:PreySensorSystem(),
            PREDATOR.type:PredatorSensorSystem()
        }

    
        self.creatures = []
        dna_preys=[]
        dna_predators=[]
        for files in OS.listdir("./saves/preys/"):
            with open("./saves/preys/"+files) as f:
                new_dna = DNA.load(f.read())
                dna_preys.append(new_dna)

        for files in OS.listdir("./saves/predator/"):
            with open("./saves/predator/"+files) as f:
                new_dna = DNA.load(f.read())
                dna_predators.append(new_dna)

        self.create_initial_prey_population(dna_preys)
        self.create_initial_predator_population(dna_predators)

    # ----------------------------------------------------
    # Population initiale
    # ----------------------------------------------------
    def create_initial_predator_population(self, dna:list[DNA]):
        if (len(dna)>0):
            parent_predators=[]
            for adn in dna:
                new_pred = Creature(
                    adn,
                    PREDATOR.type,
                    PREDATOR.ray_count,
                    self.world.width,
                    self.world.height
                )
                parent_predators.append(new_pred)
            self.creatures=[]
            for _ in range(0, self.population_size//2):
                parent = random.choice(
                    parent_predators
                )
    
                child_dna = parent.dna.mutate(
                    rate=0.03,
                    strength=0.15
                )
    
                child = Creature(
                    child_dna,
                    PREDATOR.type,
                    PREDATOR.ray_count,
                    self.world.width,
                    self.world.height
                )
    
                self.creatures.append(
                    child
                )
                

        else:
            input_size = (
                PREDATOR.ray_count * 3+PREDATOR.memory_size+PREDATOR.metrics_size
            )

            dna_size = NeuralNetwork.dna_size(
                input_size
            )

            self.creatures = []

            for _ in range(self.population_size//2):
                if self.starting_dna is not None:
                    dna = DNA.load(self.starting_dna)
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
                    PREDATOR.type,
                    PREDATOR.ray_count,
                    self.world.width,
                    self.world.height
                )

                self.creatures.append(
                    creature
                )

        self.world.creatures.extend(self.creatures)

        self.world.foods.clear()

        self.world.spawn_food(
            self.food_amount
        )

    def create_initial_prey_population(self, dna=[]):
        if len(dna)>0:
            parent_preys=[]
            for adn in dna:
                new_prey = Creature(
                    adn,
                    PREY.type,
                    PREY.ray_count,
                    self.world.width,
                    self.world.height
                )
                parent_preys.append(new_prey)
            self.creatures = []
            
            for _ in range(0, self.population_size//2):
                parent = random.choice(
                    parent_preys
                )
    
                child_dna = parent.dna.mutate(
                    rate=0.03,
                    strength=0.15
                )
    
                child = Creature(
                    child_dna,
                    PREY.type,
                    PREY.ray_count,
                    self.world.width,
                    self.world.height
                )
    
                self.creatures.append(
                    child
                )
        else:
        
            input_size = (
                PREY.ray_count * 3+PREY.memory_size+PREY.metrics_size
            )

            dna_size = NeuralNetwork.dna_size(
                input_size
            )

            self.creatures = []

            for _ in range(self.population_size//2):

                if self.starting_dna is not None:
                    dna = DNA.load(self.starting_dna)
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
                    PREY.type,
                    PREY.ray_count,
                    self.world.width,
                    self.world.height
                )

                self.creatures.append(
                    creature
                )

        self.world.creatures = self.creatures

        

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
        for type in self.world.dead_creatures.keys():
            for creature in self.world.dead_creatures[type]:
                self.logger.log_death(
                                    DeathRecord(creature, self.world.time),
                                    self.world.time,
                                    self.generation,
                                    cause="energy_depleted"
                                )

        population = self.world.creatures

        preys=[]
        predators=[]


        if len(population) == 0:

            print("Extinction totale")

            preys=self.world.dead_creatures[PREY.type].copy()
            predators=self.world.dead_creatures[PREDATOR.type].copy()
            
            self.current_step = 0

            self.world.time = 0

        else:
            for creature in population:
                if PREY.type==creature.type:
                    preys.append(creature)

                elif PREDATOR.type==creature.type:
                    predators.append(creature)
            if len(preys)==0:
                preys=self.world.dead_creatures[PREY.type].copy()

            if len(predators)==0:
                predators=self.world.dead_creatures[PREDATOR.type].copy()

        self.world.dead_creatures={1:[],2:[]}
        

        preys.sort(
            key=lambda c: c.fitness,
            reverse=True
        )

        predators.sort(
            key=lambda c: c.fitness,
            reverse=True
        )


        preys_survivors_count = max(
            1,
            int(len(preys) * 0.1)
        )

        predator_survivors_count = max(
                1,
                int(len(predators) * 0.1)
            )
        survivors_preys = preys[:preys_survivors_count]
        survivors_predator = predators[:predator_survivors_count]

        print("Nombre de proies : ",survivors_preys.__len__())
        print("Nombre de prédateurs : ", survivors_predator.__len__())
        
        for files in OS.listdir("./saves/preys/"):
            OS.remove("./saves/preys/"+files)

        for files in OS.listdir("./saves/predator/"):
            OS.remove("./saves/predator/"+files)

        for lives in survivors_preys:
            with open(f"saves/preys/{DataClass.NAMELIST[random.randint(0, DataClass.NAMELIST.__len__()-1)]}.dna", "w") as f:
                f.write(lives.dna.dump())

        for lives in survivors_predator:
            with open(f"saves/predator/{DataClass.NAMELIST[random.randint(0, DataClass.NAMELIST.__len__()-1)]}.dna", "w") as f:
                f.write(lives.dna.dump())




        print(
            f"Génération {self.generation} | "
            f"Best scores : \n\tPrey : {survivors_preys[0].fitness}\n\tPredator : {survivors_predator[0].fitness}"
        )

        


        new_population = []

        while len(new_population) < self.population_size//2:

            parent = random.choice(
                survivors_preys
            )

            child_dna = parent.dna.mutate(
                rate=0.03,
                strength=0.15
            )

            child = Creature(
                child_dna,
                PREY.type,
                PREY.ray_count,
                self.world.width,
                self.world.height
            )

            new_population.append(
                child
            )

        while len(new_population) < self.population_size:
        
            parent = random.choice(
                survivors_predator
            )

            child_dna = parent.dna.mutate(
                rate=0.03,
                strength=0.15
            )

            child = Creature(
                child_dna,
                PREDATOR.type,
                PREDATOR.ray_count,
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
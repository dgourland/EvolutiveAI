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
from App.utils.logger import SimulationLogger
from App.sensors.sensors import SensorSystem
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
        SAVE_PATH="./saves/default"
        
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

        self.SAVE_PATH=SAVE_PATH
        self.creatures = []
        dna_preys=[]
        dna_predators=[]
        if not OS.path.exists(SAVE_PATH):
            OS.mkdir(SAVE_PATH)
        if OS.path.exists(f"{SAVE_PATH}/predators.dna"):
            with open(f"{SAVE_PATH}/predators.dna") as f:
                for dna in f.read().split("\n"):
                    dna_preys.append(DNA.load(dna))

        if OS.path.exists(f"{SAVE_PATH}/predators.dna"):
            with open(f"{SAVE_PATH}/predators.dna") as f:
                for dna in f.read().split("\n"):
                    dna_predators.append(DNA.load(dna))

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
                    PREDATOR.memory_size,
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
                    PREDATOR.memory_size,
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
                    PREDATOR.memory_size,
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
                    PREY.memory_size,
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
                    PREY.memory_size,
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
                    PREY.memory_size,
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
        self.world.dead_creatures[1].sort(
            key=lambda c: c.fitness,
            reverse=True
        )
        self.world.dead_creatures[2].sort(
                key=lambda c: c.fitness,
                reverse=True
            )
        for type in self.world.dead_creatures.keys():
            for creature in self.world.dead_creatures[type]:
                self.logger.log_death(
                                    DeathRecord(creature, self.world.time),
                                    self.world.time,
                                    self.generation,
                                    cause="energy_depleted"
                                )
        self.logger.save(self.generation, self.SAVE_PATH)
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
            preys_input_size = (
                            PREY.ray_count * 3+PREY.memory_size+PREY.metrics_size
                        )
            if len(preys)<((self.population_size/2)*0.1):
                for _ in range(int((self.population_size/2)*0.1-len(preys))):
                    dna = DNA.random(NeuralNetwork.dna_size(preys_input_size))
                    prey = Creature(
                        dna,
                        creature_type=PREY.type,
                        memory_size=PREY.memory_size,
                        ray_count=PREY.ray_count,
                        world_width=self.world.width,
                        world_height=self.world.height
                    )
                    preys.append(prey)

            predator_input_size = (
                    PREDATOR.ray_count * 3+PREDATOR.memory_size+PREDATOR.metrics_size
                )
            if len(predators)<((self.population_size/2)*0.1):
                for _ in range(int((self.population_size/2)*0.1-len(predators))):
                    dna = DNA.random(NeuralNetwork.dna_size(predator_input_size))
                    predator = Creature(
                        dna,
                        creature_type=PREDATOR.type,
                        memory_size=PREDATOR.memory_size,
                        ray_count=PREDATOR.ray_count,
                        world_height=self.world.height,
                        world_width=self.world.width
                    )
                    predators.append(predator)
            
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
        
        if (OS.path.exists(f"{self.SAVE_PATH}/preys.dna")):
            OS.remove(f"{self.SAVE_PATH}/preys.dna")

        if (OS.path.exists(f"{self.SAVE_PATH}/predators.dna")):
            OS.remove(f"{self.SAVE_PATH}/predators.dna")

        
        with open(f"{self.SAVE_PATH}/preys.dna", "a") as f:
            for lives in survivors_preys:
                f.write(lives.dna.dump())

        
        with open(f"{self.SAVE_PATH}/predators.dna", "a") as f:
            for lives in survivors_predator:
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
                PREY.memory_size,
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
                PREDATOR.memory_size,
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
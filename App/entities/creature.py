"""
App/entities/creature.py

Entité vivante de la simulation.

Une créature possède :

- un ADN
- un cerveau
- des capteurs
- une énergie
- une position
- une direction

Le comportement est entièrement
déterminé par son réseau neuronal.
"""


import math
import random
import numpy as np


from App.genetics.dna import DNA
from App.brain.neural_network import NeuralNetwork
import time
from App.vars import PREY, PREDATOR


class Creature:


    def __init__(
        self,
        dna: DNA,
        creature_type,
        ray_count: int,
        world_width: int,
        world_height: int,
    ):
        # ==========================================================
        # Identité
        # ==========================================================

        self.type = creature_type
        self.dna = dna

        self.world_width = world_width
        self.world_height = world_height

        self.last_ray_query = -1

        # ==========================================================
        # Capteurs
        # ==========================================================

        self.ray_count = ray_count
        self.vision_size = ray_count * 3

        # ==========================================================
        # Métriques internes
        #
        # energy
        # speed
        # age
        # sin(angle)
        # cos(angle)
        # ==========================================================

        self.metrics_size = 5

        # ==========================================================
        # Mémoire interne
        # ==========================================================

        self.memory_size = 16

        self.memory = np.zeros(
            self.memory_size,
            dtype=np.float32
        )

        # ==========================================================
        # Entrées du réseau
        # ==========================================================

        self.input_size = (
            self.vision_size
            + self.metrics_size
            + self.memory_size
        )

        self.inputs = np.zeros(
            self.input_size,
            dtype=np.float32
        )

        # ==========================================================
        # Position
        # ==========================================================

        self.x = random.uniform(
            0,
            world_width
        )

        self.y = random.uniform(
            0,
            world_height
        )

        self.angle = random.uniform(
            0,
            math.tau
        )

        # ==========================================================
        # Caractéristiques physiques
        # ==========================================================

        if self.type == PREY.type:

            self.radius = PREY.radius
            self.max_speed = 5
            self.max_energy = 150

        else:

            self.radius = PREDATOR.radius
            self.max_speed = 3
            self.max_energy = 200

        self.speed = 0.0
        self.distance_travel = 0.0

        # ==========================================================
        # Etat biologique
        # ==========================================================

        self.object_id = 0 
        
        self.energy = self.max_energy * 0.5

        self.age = 0

        self.score = 0

        self.childs = 0

        self.wantbreed = False

        self.isalive = True

        self.fitness = 0.0

        # ==========================================================
        # Cerveau
        # ==========================================================

        self.brain = NeuralNetwork(
            dna=dna.genes,
            input_size=self.input_size,
            memory_size=self.memory_size
        )

        self.outputs = np.zeros(
            5,
            dtype=np.float32
        )

    def update_all(self, world):
        self.update_sensor(world)
        self.update_brain()
        self.update_movement()
        self.update_breeding(world)
        
    def update_sensor(self, world):

        world.sensor_system[self.type].scan(
            
                self,
                world
            )

    def update_brain(self):
        """
        Construit les entrées du réseau neuronal puis
        calcule les actions et le nouvel état mémoire.
        """

        offset = self.vision_size

        # -------------------------------------------------
        # Etat interne
        # -------------------------------------------------

        self.inputs[offset] = self.energy / self.max_energy
        self.inputs[offset + 1] = self.speed / self.max_speed

        # âge normalisé
        self.inputs[offset + 2] = min(
            self.age / 5000,
            1.0
        )

        # orientation
        self.inputs[offset + 3] = math.sin(self.angle)
        self.inputs[offset + 4] = math.cos(self.angle)

        # -------------------------------------------------
        # Mémoire
        # -------------------------------------------------

        self.inputs[
            offset + self.metrics_size:
        ] = self.memory

        # -------------------------------------------------
        # Calcul neuronal
        # -------------------------------------------------

        self.outputs, self.memory = self.brain.forward(
            inputs=self.inputs,
            memory=self.memory
        )

    def update_movement(self):

        self.act(
            self.outputs
        )

        self.move()
        if (self.type==PREY.type):
            self.energy -= (
                abs(self.speed) * 0.01
            )
        elif (self.type==PREDATOR.type):
            self.energy -= (
                0.02
                +
                abs(self.speed) * 0.02
            )

    def update_breeding(self, world):
        if self.energy>100 and self.wantbreed:
            self.energy=self.energy-100
            self.childs+=1
            child=Creature(
                self.dna.mutate(
                    rate=0.02,
                    strength=0.15
                ),
                self.type,
                self.ray_count,
                world.width,
                world.height
            )
            child.setPos(self.x+random.randint(0, 5)-random.randint(0, 5), self.y+random.randint(0, 5)-random.randint(0, 5), self.angle+random.randint(0, 5)-random.randint(0, 5))
            world.add_creature(
                child    
            )

    # ----------------------------------------------------
    # Boucle de vie
    # ----------------------------------------------------

    def update(self, world):
        self.age += 1
        self.update_sensor(world)
        self.update_brain()
        self.update_movement()
        

    def consume(self):
        self.isalive=False

    # ----------------------------------------------------
    # Décisions
    # ----------------------------------------------------

    def act(self, outputs):
        """
        Interprète les sorties du réseau neuronal.

        Sorties :
            0 : tourner à gauche
            1 : tourner à droite
            2 : accélérer
            3 : freiner
            4 : reproduction
        """

        # -------------------------------------------------
        # Rotation
        # -------------------------------------------------

        turn = outputs[1] - outputs[0]

        self.angle += turn * 0.15

        # Normalise l'angle entre 0 et 2π
        self.angle %= math.tau

        # Le fait de tourner consomme un peu d'énergie
        self.energy -= abs(turn) * 0.01

        # -------------------------------------------------
        # Accélération
        # -------------------------------------------------

        self.speed += outputs[2] * 0.2

        # -------------------------------------------------
        # Freinage
        # -------------------------------------------------

        self.speed -= outputs[3] * 0.1

        # -------------------------------------------------
        # Limitation de la vitesse
        # -------------------------------------------------

        self.speed = np.clip(
            self.speed,
            -self.max_speed,
            self.max_speed
        )

        # -------------------------------------------------
        # Reproduction
        # -------------------------------------------------

        self.wantbreed = outputs[4] > 0



    # ----------------------------------------------------
    # Déplacement
    # ----------------------------------------------------

    def move(self):
        dx=math.cos(self.angle) * self.speed
        dy=math.sin(self.angle) * self.speed
        self.x += dx
        self.y += dy

        self.x %= self.world_width
        self.y %= self.world_height

        self.distance_travel += math.hypot(dx, dy)

    # ----------------------------------------------------
    # Nourriture
    # ----------------------------------------------------

    def eat(
        self,
        food
    ):

        if self.energy > self.max_energy:

            self.energy = self.max_energy

        else:
            self.energy += food.energy
            
            self.score += 1

        



    # ----------------------------------------------------
    # Mort
    # ----------------------------------------------------

    def alive(self):
        self.fitness = (
                    self.childs*100
                    + self.score * 50
                    - self.age * 0.02
                    + self.distance_travel * 0.01
                )
        self.isalive = (self.energy>0)&self.isalive
        return self.isalive



    # ----------------------------------------------------
    # Collision cercle
    # ----------------------------------------------------

    def distance_to(
        self,
        obj
    ):

        dx = obj.x - self.x

        dy = obj.y - self.y


        return math.sqrt(
            dx*dx +
            dy*dy
        )
    def setPos(self, x, y, angle):
        self.x=x
        self.y=y
        self.angle=angle
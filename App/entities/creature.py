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
        dna,
        creature_type,
        ray_count,
        world_width,
        world_height
    ):
        
        self.type=creature_type
        self.last_ray_query=-1
        self.dna = dna
        self.input_size = ray_count * 3
        self.inputs = np.zeros(self.input_size, dtype=np.float32)
        self.ray_count=ray_count
        # ------------------------------------------------
        # Physique
        # ------------------------------------------------
        self.world_height=world_height
        self.world_width=world_width
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
            math.pi * 2
        )

        if self.type==PREY.type:
            self.radius =PREY.radius
        elif self.type==PREDATOR.type:
            self.radius=PREDATOR.radius


        self.speed = 0

        self.distance_travel=0
        if PREY.type==self.type:
            self.max_speed = 5
        if PREDATOR.type==self.type:
            self.max_speed=3



        # ------------------------------------------------
        # Vie
        # ------------------------------------------------

        self.energy = 100
        if PREY.type==self.type:
            self.max_energy=200
        if PREDATOR.type==self.type:
            self.max_energy=300

        self.age = 0
        self.childs = 0
        self.isalive=True
        self.score = 0
        self.fitness = (
            self.childs * 200
            + self.score * 100
            - self.age * 0.1
            + self.distance_travel * 0.01
        )


        # ------------------------------------------------
        # Cerveau
        # ------------------------------------------------


        self.brain = NeuralNetwork(

            dna.genes,

            self.input_size

        )

    def update_sensor(self, world):

        world.sensor_system[self.type].scan(
            self
        )

    def update_brain(self):

        self.outputs = self.brain.forward(
            self.inputs
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
                0.05
                +
                abs(self.speed) * 0.02
            )

    def update_breeding(self, world):
        if self.energy>=175:
            self.energy=50
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

    def act(
        self,
        outputs
    ):


        """
        outputs :

        0 : tourner gauche
        1 : tourner droite
        2 : accélérer
        3 : freiner
        4 : manger
        """


        turn_left = outputs[0]

        turn_right = outputs[1]


        acceleration = outputs[2]


        brake = outputs[3]



        rotation = (
            turn_right
            -
            turn_left
        )


        self.angle += (
            rotation
            *
            0.15
        )
        self.energy-=abs(rotation*0.05)


        self.speed += (
            acceleration
            *
            0.2
        )


        self.speed -= (
            brake
            *
            0.1
        )



        self.speed = max(
            -self.max_speed,
            min(
                self.speed,
                self.max_speed
            )
        )



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
                    self.childs*200
                    + self.score * 100
                    - self.age * 0.1
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
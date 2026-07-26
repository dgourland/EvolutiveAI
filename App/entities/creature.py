"""
creature.py

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


class Creature:


    def __init__(
        self,
        dna,
        ray_count,
        world_width,
        world_height
    ):

        self.last_ray_query=-1
        self.dna = dna
        self.input_size = ray_count * 2

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


        self.radius = 10


        self.speed = 0

        self.distance_travel=0
        self.max_speed = 3

        self.type=2

        # ------------------------------------------------
        # Vie
        # ------------------------------------------------

        self.energy = 100


        self.age = 0


        self.score = 0
        self.fitness = (
            self.score * 100
            + self.age * 0.1
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

        self.inputs = world.sensor_system.scan(
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

        self.energy -= (
            0.15
            +
            abs(self.speed) * 0.02
        )

    # ----------------------------------------------------
    # Boucle de vie
    # ----------------------------------------------------

    def update(self, world):

        self.age += 1

        self.update_sensor(world)

        self.update_brain()

        self.update_movement()


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

        



        if self.energy > 100:

            self.energy = 100
        else:
            self.energy += 40
            
            self.score += 1



    # ----------------------------------------------------
    # Mort
    # ----------------------------------------------------

    def alive(self):
        self.fitness = (
                    self.score * 100
                    - self.age * 0.1
                    + self.distance_travel * 0.01
                )
        return (
            self.energy > 0
        )



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
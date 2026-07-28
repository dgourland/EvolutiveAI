"""
sensors.py

Système de perception des créatures.

Transforme le monde visible en données
pour le réseau neuronal.

Chaque rayon retourne 3 valeurs :

    nourriture
    créature
    obstacle


Exemple avec 9 rayons :

9 rayons x 3 valeurs = 27 entrées neuronales
"""


import math
import numpy as np
from App.vars import *



class SensorSystem:


    def __init__(
        self,
        raycaster,
        ray_count=12,
        field_of_view=90,
        max_distance=200
    ):

        self.raycaster = raycaster

        self.ray_count = ray_count

        self.fov = math.radians(
            field_of_view
        )

        self.max_distance = max_distance

        # Cache ray angles
        if self.ray_count == 1:

            self.ray_angles = [0.0]

        else:

            self.ray_angles = np.linspace(
                -self.fov / 2,
                self.fov / 2,
                self.ray_count
            )
        self.input_buffer = np.zeros(
            self.ray_count * 3,
            dtype=np.float32
        )

    # -----------------------------------------------------
    # Scan complet
    # -----------------------------------------------------

    def scan(self, creature):

        index = 0

        for relative_angle in self.ray_angles:

            angle = (
                creature.angle
                +
                relative_angle
            )

            food, prey, other = self.cast_sensor_ray(
                creature,
                angle
            )

            self.input_buffer[index] = food
            self.input_buffer[index + 1] = prey
            self.input_buffer[index + 2] = other

            index += 3


        return self.input_buffer.copy()

    # -----------------------------------------------------
    # Rayon individuel
    # -----------------------------------------------------

    def cast_sensor_ray(
        self,
        creature,
        angle
    ):

        hit = self.raycaster.cast(
            origin=(creature.x, creature.y),
            angle=angle,
            max_distance=self.max_distance,
            ignore=creature
        )

        if hit is None:
            return (
                0.0,
                0.0,
                0.0
            )

        strength = 1.0 - hit.distance / self.max_distance

        obj_type = hit.object.type

        food = 0.0
        selfspecies = 0.0
        other = 0.0

        if obj_type == FOOD.type:
            food = strength

        elif obj_type == creature.type:
            selfspecies = strength

        else:
            other = strength

        return (
            food,
            selfspecies,
            other
        )



            
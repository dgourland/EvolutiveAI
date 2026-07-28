"""
App/sensors/sensors.py

Système de perception optimisé.

Le scan écrit directement dans
le buffer mémoire de la créature.

Aucune allocation pendant la simulation.
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


        # Angles relatifs des rayons

        if ray_count == 1:

            self.ray_angles = [0.0]

        else:

            step = self.fov / (ray_count - 1)

            start = -self.fov / 2

            self.ray_angles = [
                start + i * step
                for i in range(ray_count)
            ]



    # -----------------------------------------------------
    # Scan complet
    # -----------------------------------------------------

    def scan(self, creature):


        inputs = creature.inputs


        index = 0


        base_angle = creature.angle


        ox = creature.x
        oy = creature.y



        for relative_angle in self.ray_angles:


            angle = (
                base_angle
                +
                relative_angle
            )


            hit = self.raycaster.cast(
                ox,
                oy,
                angle,
                self.max_distance,
                creature
            )


            if hit is None:

                inputs[index] = 0.0
                inputs[index + 1] = 0.0
                inputs[index + 2] = 0.0


            else:

                obj, distance = hit


                strength = (
                    1.0
                    -
                    distance / self.max_distance
                )


                obj_type = obj.type



                if obj_type == FOOD.type:

                    inputs[index] = strength
                    inputs[index + 1] = 0.0
                    inputs[index + 2] = 0.0


                elif obj_type == creature.type:

                    inputs[index] = 0.0
                    inputs[index + 1] = strength
                    inputs[index + 2] = 0.0


                else:

                    inputs[index] = 0.0
                    inputs[index + 1] = 0.0
                    inputs[index + 2] = strength



            index += 3



        return inputs
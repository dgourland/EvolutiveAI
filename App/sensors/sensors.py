"""
App/sensors/sensors.py

Système de perception optimisé.

Le scan écrit directement dans
le buffer mémoire de la créature.

Optimisations :

- aucun calcul trigonométrique par rayon
- aucun tableau temporaire
- vecteurs des rayons pré-calculés
"""

import math

from App.vars import FOOD


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

        self.max_distance = max_distance

        self.fov = math.radians(field_of_view)

        # -------------------------------------------------
        # Pré-calcul des angles
        # -------------------------------------------------

        if ray_count <= 1:

            self.ray_angles = [0.0]

        else:

            step = self.fov / (ray_count - 1)
            start = -self.fov * 0.5

            self.ray_angles = [
                start + i * step
                for i in range(ray_count)
            ]

        # -------------------------------------------------
        # Pré-calcul des vecteurs unitaires
        # -------------------------------------------------

        self.relative_vectors = [

            (
                math.cos(angle),
                math.sin(angle)
            )

            for angle in self.ray_angles

        ]

    # -----------------------------------------------------
    # Scan complet
    # -----------------------------------------------------

    def scan(self, creature):

        inputs = creature.inputs

        ox = creature.x
        oy = creature.y

        # Rotation de la créature
        cos_angle = math.cos(creature.angle)
        sin_angle = math.sin(creature.angle)

        index = 0

        for rel_dx, rel_dy in self.relative_vectors:

            # Rotation du vecteur du rayon
            dx = rel_dx * cos_angle - rel_dy * sin_angle
            dy = rel_dx * sin_angle + rel_dy * cos_angle

            hit = self.raycaster.cast_vector(
                ox=ox,
                oy=oy,
                dx=dx,
                dy=dy,
                max_distance=self.max_distance,
                ignore=creature
            )

            # Réinitialisation des 3 entrées du rayon
            inputs[index] = 0.0
            inputs[index + 1] = 0.0
            inputs[index + 2] = 0.0

            if hit is not None:

                obj, distance = hit

                strength = 1.0 - distance / self.max_distance

                if obj.type == FOOD.type:

                    inputs[index] = strength

                elif obj.type == creature.type:

                    inputs[index + 1] = strength

                else:

                    inputs[index + 2] = strength

            index += 3

        return inputs
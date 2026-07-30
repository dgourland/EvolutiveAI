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

import math, time

from App.vars import FOOD, PREY, PREDATOR
from App.physics.jit_math import njit_scan
import numpy as np


class SensorSystem:

    def __init__(
        self,
        ray_count=9,
        fov=math.pi * 0.8,
        max_distance=200,
        
    ):

        self.ray_count = ray_count
        self.max_distance = max_distance
        self.fov = fov

        self.query_id = 0


        self.relative_vectors = np.zeros(
            (ray_count, 2),
            dtype=np.float32
        )


        half_fov = fov * 0.5


        for i in range(ray_count):

            if ray_count == 1:
                angle = 0.0

            else:
                angle = (
                    -half_fov
                    +
                    i * fov / (ray_count - 1)
                )


            self.relative_vectors[i,0] = math.cos(angle)
            self.relative_vectors[i,1] = math.sin(angle)
    # -----------------------------------------------------
    # Scan complet
    # -----------------------------------------------------

    def scan(self, creature, world):

        # ---------------------------------
        # Creature state
        # ---------------------------------

        ox = creature.x
        oy = creature.y

        cos_angle = math.cos(creature.angle)
        sin_angle = math.sin(creature.angle)


        # ---------------------------------
        # Sensor input buffer
        # ---------------------------------

        inputs = creature.inputs


        # ---------------------------------
        # World buffers
        # ---------------------------------

        object_x = world.object_x
        object_y = world.object_y
        object_radius = world.object_radius
        object_type = world.object_type

        object_ids = world.spatial_grid.object_ids

        cell_start = world.spatial_grid.cell_start
        cell_end = world.spatial_grid.cell_end


        # ---------------------------------
        # Unique object id to ignore
        # ---------------------------------

        ignore_id = creature.object_id


        # ---------------------------------
        # Query cache
        # ---------------------------------

        query_id = self.query_id


        # ---------------------------------
        # Run JIT scanner
        # ---------------------------------

        njit_scan(
            ox,
            oy,

            cos_angle,
            sin_angle,

            self.relative_vectors,

            self.max_distance,


            object_ids,
            cell_start,
            cell_end,


            object_x,
            object_y,
            object_radius,
            object_type,


            world.object_last_query,
            query_id,


            ignore_id,


            world.spatial_grid.ray_stamp,
            world.spatial_grid.current_ray,

            world.spatial_grid.grid_width,
            world.spatial_grid.grid_height,
            world.spatial_grid.cell_size,


            inputs,

            creature.type,
            FOOD.type
        )


        # ---------------------------------
        # Increment query counter
        # ---------------------------------

        self.query_id += self.ray_count


        return inputs
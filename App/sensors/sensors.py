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
from App.entities.creature import Creature


class SensorSystem:
    query_id = 0

    @staticmethod
    def scan(creature:Creature, world):

        # ---------------------------------
        # Creature state
        # ---------------------------------
        if world.spectator>=0:
            is_spec= world.creatures[(world.spectator)%world.creatures.__len__()]==creature
        else:
            is_spec=False
        if is_spec:
            world.spec_rays_vectors.fill(0)
            world.valid_rays = creature.ray_count
        ox = creature.x
        oy = creature.y
        
        cos_angle = math.cos(creature.angle)
        sin_angle = math.sin(creature.angle)
        relative_vectors = creature.ray_relative_vectors

        for i in range(creature.ray_count):
        
            if creature.ray_count == 1:
                angle = 0.0

            else:
                angle = (
                    -(creature.fov / 2)
                    +
                    i * creature.fov / (creature.ray_count - 1)
                )


            relative_vectors[i,0] = math.cos(angle)
            relative_vectors[i,1] = math.sin(angle)

        # ---------------------------------
        # Sensor input buffer
        # ---------------------------------

        inputs = creature.inputs


        # ---------------------------------
        # World buffers
        # ---------------------------------

        object_x = world.object_data[:,0]
        object_y = world.object_data[:,1]
        object_radius = world.object_data[:,2]
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

        query_id = SensorSystem.query_id


        # ---------------------------------
        # Run JIT scanner
        # ---------------------------------
        if is_spec:
            world.valid_rays=creature.ray_count

            
        njit_scan(
            ox,
            oy,

            cos_angle,
            sin_angle,

            creature.ray_relative_vectors,

            creature.max_distance,


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
            FOOD.type,
            is_spec,
            world.spec_rays_vectors

        )


        # ---------------------------------
        # Increment query counter
        # ---------------------------------

        SensorSystem.query_id += creature.ray_count


        return inputs
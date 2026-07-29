"""
App/physics/raycaster.py

Système de raycasting optimisé.

Utilise SpatialGrid pour limiter
le nombre d'objets testés.

Deux modes :

cast()
    reçoit un angle (compatibilité)

cast_vector()
    reçoit directement un vecteur directionnel
    (utilisé par les capteurs optimisés)

Retour :

    (objet_touché, distance)

ou

    None
"""


import math


class Raycaster:


    def __init__(
        self,
        spatial_grid,
        step=5
    ):

        self.grid = spatial_grid

        self.query_id = 0



    # -----------------------------------------------------
    # Version classique avec angle
    # -----------------------------------------------------

    def cast(
        self,
        ox,
        oy,
        angle,
        max_distance,
        ignore=None
    ):

        dx = math.cos(angle)
        dy = math.sin(angle)

        return self.cast_vector(
            ox,
            oy,
            dx,
            dy,
            max_distance,
            ignore
        )



    # -----------------------------------------------------
    # Version optimisée avec vecteur
    # -----------------------------------------------------

    def cast_vector(
        self,
        ox,
        oy,
        dx,
        dy,
        max_distance,
        ignore=None
    ):


        self.query_id += 1

        query_id = self.query_id


        closest_object = None

        closest_distance = max_distance



        for cell, cell_distance in self.grid.ray_cells(
            ox,
            oy,
            dx,
            dy,
            max_distance
        ):


            # Les cellules suivantes sont forcément
            # plus éloignées

            if cell_distance > closest_distance:

                break



            for obj in self.grid.query_cell(
                *cell
            ):


                if obj is ignore:

                    continue



                # Un objet peut être présent
                # dans plusieurs cellules

                if obj.last_ray_query == query_id:

                    continue


                obj.last_ray_query = query_id



                hit_distance = self.ray_hits_circle(
                    ox,
                    oy,
                    dx,
                    dy,
                    obj,
                    closest_distance
                )



                if hit_distance is not None:


                    closest_distance = hit_distance

                    closest_object = obj



        if closest_object is None:

            return None



        return (
            closest_object,
            closest_distance
        )



    # -----------------------------------------------------
    # Collision rayon / cercle
    # -----------------------------------------------------

    def ray_hits_circle(
        self,
        ox,
        oy,
        dx,
        dy,
        obj,
        max_distance
    ):


        vx = obj.x - ox
        vy = obj.y - oy



        # Projection du centre
        # sur le rayon

        projection = (
            vx * dx
            +
            vy * dy
        )



        if projection < 0 or projection > max_distance:

            return None



        closest_x = (
            ox
            +
            dx * projection
        )

        closest_y = (
            oy
            +
            dy * projection
        )



        diff_x = obj.x - closest_x
        diff_y = obj.y - closest_y



        distance_squared = (
            diff_x * diff_x
            +
            diff_y * diff_y
        )



        radius = obj.radius



        if distance_squared > radius * radius:

            return None



        offset = math.sqrt(
            radius * radius
            -
            distance_squared
        )



        hit_distance = projection - offset



        if hit_distance < 0:

            hit_distance = projection



        return hit_distance
"""
raycaster.py

Système de raycasting pour la simulation.

Le raycaster utilise une SpatialGrid
pour trouver rapidement les objets sur le chemin
d'un rayon.

Un objet détectable doit posséder :

    x
    y
    radius
    type
"""


from dataclasses import dataclass
import math



# ---------------------------------------------------------
# Résultat d'un rayon
# ---------------------------------------------------------

@dataclass
class RaycastHit:

    object: object

    distance: float

    x: float

    y: float



# ---------------------------------------------------------
# Raycaster
# ---------------------------------------------------------

class Raycaster:


    def __init__(
        self,
        spatial_grid,
        step=5
    ):

        self.grid = spatial_grid

        self.step = step
        self.query_id = 0
        self.checked = {}



    # -----------------------------------------------------
    # Raycast principal
    # -----------------------------------------------------

    def cast(
        self,
        origin,
        angle,
        max_distance,
        ignore=None
    ):

        ox, oy = origin

        dx = math.cos(angle)
        dy = math.sin(angle)


        self.query_id += 1
        query_id = self.query_id


        closest_hit = None
        closest_distance = max_distance



        for cell, distance in self.grid.ray_cells(
            ox,
            oy,
            dx,
            dy,
            max_distance
        ):

            for obj in self.grid.query_cell(*cell):


                if obj is ignore:
                    continue


                if obj.last_ray_query == query_id:
                    continue


                obj.last_ray_query = query_id



                hit_distance = self.ray_hits_circle(
                    ox,
                    oy,
                    dx,
                    dy,
                    obj,
                    max_distance
                )


                if hit_distance is not None and hit_distance < closest_distance:

                    closest_distance = hit_distance


                    closest_hit = RaycastHit(
                        object=obj,
                        distance=hit_distance,
                        x=ox + dx * hit_distance,
                        y=oy + dy * hit_distance
                    )



        return closest_hit



    # -----------------------------------------------------
    # Collision point / cercle
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
        """
        Test précis intersection rayon / cercle.

        Retourne la distance d'impact
        ou None si aucune collision.
        """

        # vecteur origine -> centre objet

        vx = obj.x - ox
        vy = obj.y - oy


        # projection du centre sur le rayon

        t = (
            vx * dx
            +
            vy * dy
        )


        # objet derrière le rayon

        if t < 0 or t > max_distance:
            return None



        # point le plus proche sur le rayon

        closest_x = ox + dx * t
        closest_y = oy + dy * t



        # distance entre ce point et le cercle

        dist_x = obj.x - closest_x
        dist_y = obj.y - closest_y


        distance_squared = (
            dist_x * dist_x
            +
            dist_y * dist_y
        )



        # pas de collision

        if distance_squared > obj.radius * obj.radius:
            return None



        # vraie distance du bord du cercle

        offset = math.sqrt(
            obj.radius * obj.radius
            -
            distance_squared
        )


        hit_distance = t - offset


        return hit_distance
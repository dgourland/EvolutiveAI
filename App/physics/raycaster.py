import math
from App.physics.jit_math import ray_circle_test
from App.physics.jit_math import raycast_objects
class Raycaster:


    def __init__(
        self,
        spatial_grid,
        world
    ):

        self.grid = spatial_grid

        self.world = world

        self.query_id = 0



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


        xs = self.world.object_x
        ys = self.world.object_y
        radii = self.world.object_radius
        last_query = self.world.object_last_query


        closest_object = -1
        closest_distance = max_distance



        for cell_id, cell_distance in self.grid.ray_cells(
            ox,
            oy,
            dx,
            dy,
            max_distance
        ):

            if cell_distance > closest_distance:
                break

            objects, start, end = self.grid.query_cell(cell_id)

            object_id, distance = raycast_objects(
                ox,
                oy,
                dx,
                dy,
                closest_distance,
                objects,
                start,
                end,
                xs,
                ys,
                radii
            )


            if object_id >= 0:

                closest_object = object_id
                closest_distance = distance

        if closest_object == -1:
            return None


        return (
            closest_object,
            closest_distance
        )

import math
import numpy as np


class SensorSystem:


    def __init__(
        self,
        raycaster,
        ray_count=9,
        field_of_view=180,
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


        # New input size:
        #
        # every ray:
        # strength
        # type
        #
        self.input_buffer = np.zeros(
            self.ray_count * 2,
            dtype=np.float32
        )



    def scan(
        self,
        creature
    ):


        index = 0


        for relative_angle in self.ray_angles:


            angle = (
                creature.angle
                +
                relative_angle
            )


            strength, obj_type = self.cast_sensor_ray(
                creature,
                angle
            )


            self.input_buffer[index] = strength

            self.input_buffer[index+1] = obj_type


            index += 2



        return self.input_buffer.copy()



    def cast_sensor_ray(
        self,
        creature,
        angle
    ):


        hit = self.raycaster.cast(

            origin=(
                creature.x,
                creature.y
            ),

            angle=angle,

            max_distance=self.max_distance,

            ignore=creature
        )



        # Nothing detected

        if hit is None:

            return (
                0.0,
                0.0
            )



        strength = (
            1.0
            -
            hit.distance
            /
            self.max_distance
        )


        obj = hit.object



        if obj.type == "food":

            return (
                strength,
                1.0
            )


        elif obj.type == "creature":

            return (
                strength,
                2.0
            )


        elif obj.type == "obstacle":

            return (
                strength,
                3.0
            )


        return (
            0.0,
            0.0
        )
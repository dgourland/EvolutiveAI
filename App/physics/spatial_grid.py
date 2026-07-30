"""
Spatial hash grid.

Stores object IDs only.

Workflow:

1. clear()
2. insert(object_id, x, y, radius)
3. finalize()

After finalize:
cell_start[cell] : beginning index
cell_end[cell]   : ending index

Objects are stored in object_ids[start:end]
"""

import numpy as np


class SpatialGrid:


    def __init__(
        self,
        width,
        height,
        cell_size=64,
        max_objects=20000
    ):

        self.cell_size = cell_size

        self.grid_width = (
            width // cell_size
        ) + 1

        self.grid_height = (
            height // cell_size
        ) + 1


        self.cell_count = (
            self.grid_width *
            self.grid_height
        )


        self.max_objects = max_objects


        # ------------------------------------
        # Temporary build storage
        # ------------------------------------

        self.build_lists = [
            []
            for _ in range(self.cell_count)
        ]


        # ------------------------------------
        # Final compressed storage
        # ------------------------------------

        self.cell_start = np.zeros(
            self.cell_count,
            dtype=np.int32
        )

        self.cell_end = np.zeros(
            self.cell_count,
            dtype=np.int32
        )

        self.object_ids = np.zeros(
            self.max_objects,
            dtype=np.int32
        )

        self.object_count = 0


        # ------------------------------------
        # Ray traversal cache
        # ------------------------------------

        self.ray_stamp = np.zeros(
            self.cell_count,
            dtype=np.int32
        )

        self.current_ray = 0



    # ------------------------------------
    # Reset
    # ------------------------------------

    def clear(self):

        self.object_count = 0

        self.cell_start.fill(0)
        self.cell_end.fill(0)

        for cell in self.build_lists:
            cell.clear()



    # ------------------------------------
    # Insert object
    # ------------------------------------

    def insert(
        self,
        object_id,
        x,
        y,
        radius
    ):

        min_x = max(
            0,
            int((x-radius)//self.cell_size)
        )

        max_x = min(
            self.grid_width-1,
            int((x+radius)//self.cell_size)
        )


        min_y = max(
            0,
            int((y-radius)//self.cell_size)
        )

        max_y = min(
            self.grid_height-1,
            int((y+radius)//self.cell_size)
        )


        for cy in range(
            min_y,
            max_y+1
        ):

            row = cy * self.grid_width

            for cx in range(
                min_x,
                max_x+1
            ):

                self.build_lists[
                    row + cx
                ].append(
                    object_id
                )



    # ------------------------------------
    # Compress grid
    # ------------------------------------

    def finalize(self):

        index = 0


        for cell_id in range(
            self.cell_count
        ):

            self.cell_start[cell_id] = index


            for obj_id in self.build_lists[cell_id]:

                if index >= self.max_objects:
                    raise RuntimeError(
                        "SpatialGrid max_objects exceeded"
                    )

                self.object_ids[index] = obj_id
                index += 1


            self.cell_end[cell_id] = index


            self.build_lists[cell_id].clear()


        self.object_count = index



    # ------------------------------------
    # Query cell
    # ------------------------------------

    def query_cell(
        self,
        cell_id
    ):

        return (
            self.object_ids,
            self.cell_start[cell_id],
            self.cell_end[cell_id]
        )



    # ------------------------------------
    # Cells crossed by a ray
    # ------------------------------------

    def ray_cells(
        self,
        x,
        y,
        dx,
        dy,
        max_distance
    ):

        self.current_ray += 1

        ray_id = self.current_ray


        cx = int(x // self.cell_size)
        cy = int(y // self.cell_size)


        if (
            cx < 0 or
            cy < 0 or
            cx >= self.grid_width or
            cy >= self.grid_height
        ):
            return


        if dx > 0:
            step_x = 1
            next_x = (
                (cx + 1) *
                self.cell_size
            )

            t_max_x = (
                next_x - x
            ) / dx

            t_delta_x = (
                self.cell_size / dx
            )

        elif dx < 0:
            step_x = -1
            next_x = (
                cx *
                self.cell_size
            )

            t_max_x = (
                next_x - x
            ) / dx

            t_delta_x = (
                -self.cell_size / dx
            )

        else:
            step_x = 0
            t_max_x = float("inf")
            t_delta_x = float("inf")



        if dy > 0:
            step_y = 1
            next_y = (
                (cy + 1) *
                self.cell_size
            )

            t_max_y = (
                next_y - y
            ) / dy

            t_delta_y = (
                self.cell_size / dy
            )

        elif dy < 0:
            step_y = -1
            next_y = (
                cy *
                self.cell_size
            )

            t_max_y = (
                next_y - y
            ) / dy

            t_delta_y = (
                -self.cell_size / dy
            )

        else:
            step_y = 0
            t_max_y = float("inf")
            t_delta_y = float("inf")



        distance = 0.0


        while distance <= max_distance:


            cell_id = (
                cy *
                self.grid_width
                +
                cx
            )


            if self.ray_stamp[cell_id] != ray_id:

                self.ray_stamp[cell_id] = ray_id

                yield (
                    cell_id,
                    distance
                )


            if t_max_x < t_max_y:

                cx += step_x
                distance = t_max_x
                t_max_x += t_delta_x

            else:

                cy += step_y
                distance = t_max_y
                t_max_y += t_delta_y



            if (
                cx < 0 or
                cy < 0 or
                cx >= self.grid_width or
                cy >= self.grid_height
            ):
                break
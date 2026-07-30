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

    
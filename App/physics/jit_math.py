from numba import njit
import numpy as np
import math

@njit
def jit_forward(
    inputs,
    memory,
    w1,
    b1,
    w2,
    b2,
    w_action,
    b_action,
    w_memory,
    b_memory
):

    neural_input = np.empty(
        inputs.shape[0] + memory.shape[0],
        dtype=np.float32
    )

    for i in range(inputs.shape[0]):
        neural_input[i] = inputs[i]

    for i in range(memory.shape[0]):
        neural_input[inputs.shape[0] + i] = memory[i]


    hidden1 = np.tanh(
        neural_input @ w1 + b1
    )


    hidden2 = np.tanh(
        hidden1 @ w2 + b2
    )


    actions = np.tanh(
        hidden2 @ w_action + b_action
    )


    new_memory = np.tanh(
        hidden2 @ w_memory + b_memory
    )


    return actions, new_memory


@njit
def ray_circle_test(
    ox,
    oy,
    dx,
    dy,
    obj_x,
    obj_y,
    radius,
    max_distance
):

    vx = obj_x - ox
    vy = obj_y - oy


    projection = (
        vx * dx +
        vy * dy
    )


    if projection < 0 or projection > max_distance:
        return -1.0


    closest_x = (
        ox +
        dx * projection
    )

    closest_y = (
        oy +
        dy * projection
    )


    diff_x = obj_x - closest_x
    diff_y = obj_y - closest_y


    dist2 = (
        diff_x * diff_x +
        diff_y * diff_y
    )


    r2 = radius * radius


    if dist2 > r2:
        return -1.0


    offset = math.sqrt(
        r2 - dist2
    )


    hit = projection - offset


    if hit < 0:
        hit = projection


    return hit

@njit
def raycast(
    ox,
    oy,
    dx,
    dy,
    max_distance,

    cell_ids,
    cell_starts,
    cell_ends,

    object_x,
    object_y,
    object_radius,

    visited,
    query_id
):

    closest = max_distance
    result = -1


    for i in range(cell_ids.shape[0]):

        obj_id = cell_ids[i]


        if visited[obj_id] == query_id:
            continue


        visited[obj_id] = query_id


        hit = ray_circle_test(
            ox,
            oy,
            dx,
            dy,
            object_x[obj_id],
            object_y[obj_id],
            object_radius[obj_id],
            closest
        )


        if hit >= 0:

            closest = hit
            result = obj_id


    return result, closest

@njit
def ray_cells_jit(
    ox,
    oy,
    dx,
    dy,
    max_distance,
    cell_buffer,
    distance_buffer,
    grid_width,
    grid_height,
    cell_size
):

    count = 0

    cx = int(ox // cell_size)
    cy = int(oy // cell_size)

    if (
        cx < 0 or
        cy < 0 or
        cx >= grid_width or
        cy >= grid_height
    ):
        return 0


    distance = 0.0

    step = cell_size * 0.5


    while distance <= max_distance:

        if (
            cx >= 0 and
            cy >= 0 and
            cx < grid_width and
            cy < grid_height
        ):

            cell_buffer[count] = (
                cy * grid_width + cx
            )

            distance_buffer[count] = distance

            count += 1


        distance += step

        px = ox + dx * distance
        py = oy + dy * distance

        cx = int(px // cell_size)
        cy = int(py // cell_size)


        if count >= cell_buffer.shape[0]:
            break


    return count


@njit
def njit_scan(
        ox,
        oy,

        cos_angle,
        sin_angle,

        relative_vectors,

        max_distance,

        object_ids,
        cell_start,
        cell_end,

        object_x,
        object_y,
        object_radius,
        object_type,
        last_query,
        query_id,

        ignore_id,

        ray_stamp,
        current_ray,
        grid_width,
        grid_height,
        cell_size,

        inputs,
        creature_type,
        food_type
    ):
    
    
    index = 0

    for r in range(relative_vectors.shape[0]):

        rel_dx = relative_vectors[r,0]
        rel_dy = relative_vectors[r,1]

        # rotate ray
        dx = rel_dx * cos_angle - rel_dy * sin_angle
        dy = rel_dx * sin_angle + rel_dy * cos_angle


        # new query id for this ray
        query_id += 1
        ray_query = query_id


        closest_object = -1
        closest_distance = max_distance


        # temporary buffers are needed because numba cannot iterate generators
        cell_buffer = np.empty(128, dtype=np.int32)
        distance_buffer = np.empty(128, dtype=np.float32)


        cell_count = ray_cells_jit(
            ox,
            oy,
            dx,
            dy,
            max_distance,

            cell_buffer,
            distance_buffer,

            grid_width,
            grid_height,
            cell_size
        )


        for c in range(cell_count):

            cell_id = cell_buffer[c]
            cell_distance = distance_buffer[c]


            if cell_distance > closest_distance:
                break


            start = cell_start[cell_id]
            end = cell_end[cell_id]


            for i in range(start, end):

                obj_id = object_ids[i]


                if obj_id == ignore_id:
                    continue


                # avoid testing the same object several times
                if last_query[obj_id] == ray_query:
                    continue

                last_query[obj_id] = ray_query



                hit = ray_circle_test(
                    ox,
                    oy,
                    dx,
                    dy,
                    object_x[obj_id],
                    object_y[obj_id],
                    object_radius[obj_id],
                    closest_distance
                )


                if hit >= 0:

                    closest_distance = hit
                    closest_object = obj_id



        # write sensor values

        inputs[index] = 0.0
        inputs[index + 1] = 0.0
        inputs[index + 2] = 0.0


        if closest_object >= 0:

            strength = (
                1.0 -
                closest_distance / max_distance
            )


            hit_type = object_type[closest_object]


            if hit_type == food_type:

                inputs[index] = strength


            elif hit_type == creature_type:

                inputs[index + 1] = strength


            else:

                inputs[index + 2] = strength



        index += 3
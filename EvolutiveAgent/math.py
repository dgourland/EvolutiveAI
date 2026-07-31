from numba import njit
import numpy as np
import math

@njit(nopython=True)
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
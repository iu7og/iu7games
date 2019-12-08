"""
      ===== TEEN48 RUNNER v.0.1a =====
      Copyright (C) 2019 IU7Games Team.
"""

import ctypes

class matrix_t(ctypes.Structure):
    _fields_ = [("rows", ctypes.c_int),
                ("columns", ctypes.c_int),
                ("matrix_ptr", ctypes.POINTER(ctypes.POINTER(ctypes.c_int)))]

    def __init__(self, rows, columns):
        self.rows = rows
        self.columns = columns

        c_int_p = ctypes.POINTER(ctypes.c_int)
        value_array = ctypes.c_int * columns
        pointer_array = c_int_p * rows
        matrix_pointer = pointer_array()
        for i in range(4):
            matrix_pointer[i] = value_array()
            for j in range(4):
                matrix_pointer[i][j] = 0

        self.matrix_ptr = matrix_pointer




def start_teen48game_competition(players_info, field_size):
    results = []

    for player in players_info:
        player_lib = ctypes.CDLL(player)
        player_lib.teen48game.argtypes = [matrix_t]
        player_lib.teen48game.restype = ctypes.c_char
        matrix = matrix_t(field_size, field_size)

        player_lib.teen48game(matrix)
        for i in range(4):
            for j in range(4):
                print(matrix.matrix_ptr[i][j])


if __name__ == "__main__":
    start_teen48game_competition(["./teen48lib.so"], 4)

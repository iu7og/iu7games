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



def start_teen48game_competition(players_info, field_size):
    for player in players_info:
        player_lib = ctypes.CDLL(player)
        player_lib.teen48game.argtypes = [ctypes.POINTER(matrix_t)]
        player_lib.teen48game.restype = ctypes.c_char
        matrix = matrix_t(field_size, field_size)
        """
        TODO: разобраться как нормально передать поинтер на поинтер, а не сишный массив....
        ничё не работает..грустно....
        """
        #matrix.matrix_ptr = ctypes.cast(c, ctypes.POINTER(ctypes.POINTER(ctypes.c_int)))
        #q = ctypes.cast(k, ctypes.POINTER((ctypes.c_int * 4)))
        #matrix.matrix_ptr = ctypes.cast(b, ctypes.POINTER(ctypes.c_int))
        
        player_lib.teen48game(ctypes.byref(matrix))
        for i in range(4):
            for j in range(4):
                print(matrix.matrix_ptr[i][j])


if __name__ == "__main__":
    start_teen48game_competition(["./teen48lib.so"], 4)

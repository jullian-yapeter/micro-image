import numpy as np


'''
Image level data and methods
'''


class MicroImage():

    def __init__(self, rows, cols):
        self.bitscan = np.zeros((rows, cols))  # for dye
        self.border = np.zeros((rows))  # for body

    def get_bitscan(self):
        return np.copy(self.bitscan)

    def get_border(self):
        return np.copy(self.border)

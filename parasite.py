from micro_image import MicroImage
import config as cfg
import os
import numpy as np


'''
Representation of a parasite's body and dye
'''


class Parasite():

    def __init__(self, rows, cols):
        self.body = MicroImage(rows, cols)
        self.dye = MicroImage(rows, cols)
        self.has_cancer = False

    def save_data(self):
        self.save_body()
        self.save_dye()

    def calc_cancer(self):
        return

    def has_cancer(self):
        return self.__has_cancer

    def show_image(self):
        return

    def save_image(self):
        return

    def save_body_data(self):
        path = os.path.join(cfg.SAVE_DIR, "body.npy")
        np.save(path, self.body.get_border())

    def save_dye_data(self):
        path = os.path.join(cfg.SAVE_DIR, "dye.npy")
        np.save(path, self.body.get_bitscan())

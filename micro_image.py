import config as cfg
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt


'''
Image level data and methods
'''


class MicroImage():

    def __init__(self, path):
        self.raw = self.read_img(path)

    def read_img(self, path):
        return ((255-np.asarray(Image.open(path))) / 255).astype(np.uint8)

    def show_img(self):
        plt.imshow((1-self.raw)*255, cmap='gray')
        plt.show()


class ScanLinesMicroImage(MicroImage):

    def __init__(self, path):
        super().__init__(path)


class BitMapMicroImage(MicroImage):

    def __init__(self, path):
        super().__init__(path)


if __name__ == "__main__":
    path = os.path.join(cfg.COLLECTED_DIR, "raw_sess_0.png")
    body = MicroImage(path)
    body.show_img()

from micro_image import ScanLinesMicroImage, BitMapMicroImage
import config as cfg
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
import sys


'''
Representation of a parasite's body and dye
'''
class Parasite():

    def __init__(self, sess_name, path_to_body, path_to_veins, MicroImageClass):
        self.sess_name = sess_name
        self.body = MicroImageClass(path_to_body)
        self.veins = MicroImageClass(path_to_veins)
        self.vein_body_frac = self.calc_cancer()

    def calc_cancer(self):
        return np.multiply(self.body.binary_npy, self.veins.binary_npy).sum() / self.body.binary_npy.size

    def has_cancer(self):
        return self.vein_body_frac > cfg.CANCER_THRESH_PERC

    def show_image(self):
        img = np.zeros(self.body.binary_npy.shape)
        img += self.body.binary_npy * 3
        img += self.veins.binary_npy * 5
        plt.imshow(255-np.minimum(img, 255), cmap='gray')
        plt.show()

    def save_body_data(self):
        self.body.print_memory()
        self.body.save_processed_img(self.sess_name + "_body")

    def show_veins_data(self):
        self.veins.print_memory()
        self.veins.save_processed_img(self.sess_name + "_veins")

    def save_data(self):
        self.save_body_data()
        self.show_veins_data()

if __name__ == "__main__":
    par1 = Parasite("lab0",
                    os.path.join(cfg.COLLECTED_DIR, "small_sess_0_body.tiff"),
                    os.path.join(cfg.COLLECTED_DIR, "small_sess_0_veins.tiff"),
                    BitMapMicroImage)
    # par2 = Parasite("lab1",
    #                 os.path.join(cfg.COLLECTED_DIR, "small_sess_0_body.tiff"),
    #                 os.path.join(cfg.COLLECTED_DIR, "small_sess_0_veins.tiff"),
    #                 ScanLinesMicroImage)
    # par1.save_data()
    # par1.show_image()
    # print(par1.vein_body_frac)
    # print(par1.has_cancer())
    # print(par1.body.raw)
    # print(sys.getsizeof(par1.body.raw.getdata()))
    # data_seq = par1.body.raw.getdata()
    # for i in range(len(data_seq)):
    #     print(data_seq[i])
    # print(par1.body.raw.getpixel((0,0)))
    # print(sys.getsizeof(par1.body.processed))
    # print(sys.getsizeof(par2.body.processed))
    # print(sys.getsizeof(par1.body.raw.tobitmap()))
    par1.body.show_raw_img()
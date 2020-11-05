from micro_image_large import ScanLinesMicroImage, BitMapMicroImage
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
        self.veins_body_frac = self.calc_cancer()

    def calc_cancer(self):
        return self.body.calc_veins_perc(self.veins)

    def has_cancer(self):
        return self.veins_body_frac > cfg.CANCER_THRESH_PERC

    def show_image(self):
        plt.imshow(Image.blend(self.body.raw, self.veins.raw, 0.5), cmap='gray')
        plt.show()

    def save_body_data(self):
        print("BODY DATA :")
        self.body.print_memory()
        self.body.save_processed_img(self.sess_name + "_body")

    def show_veins_data(self):
        print("VEINS DATA :")
        self.veins.print_memory()
        self.veins.save_processed_img(self.sess_name + "_veins")

    def save_data(self):
        self.save_body_data()
        self.show_veins_data()

if __name__ == "__main__":
    par1 = Parasite("lab_sess_0",
                    os.path.join(cfg.COLLECTED_DIR, "lab_sess_0_rf4_body.tiff"),
                    os.path.join(cfg.COLLECTED_DIR, "lab_sess_0_rf4_veins.tiff"),
                    ScanLinesMicroImage)
    par1.show_image()
    print("Body Process & Inverse Validity:", par1.body.validate_process())
    print("Veins Process & Inverse Validity:", par1.veins.validate_process())
    print("Veins to Body %:", par1.veins_body_frac * 100)
    print("Has cancer:", par1.has_cancer())
    par1.save_data()
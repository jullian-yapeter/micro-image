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

    def __init__(self, sess_name, body_img_path, veins_img_path, MicroImageClass):
        self.sess_name = sess_name
        self.mic_name = MicroImageClass.name
        self.body = MicroImageClass(body_img_path)
        self.veins = MicroImageClass(veins_img_path)
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
        self.body.save_processed_img(self.sess_name + "_body_" + self.mic_name)

    def show_veins_data(self):
        print("VEINS DATA :")
        self.veins.print_memory()
        self.veins.save_processed_img(self.sess_name + "_veins_" + self.mic_name)

    def save_data(self):
        self.save_body_data()
        self.show_veins_data()

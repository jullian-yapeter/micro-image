from micro_image_large import ScanLinesMicroImage, BitMapMicroImage
import config as cfg
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
import sys


'''
Class to represent and process images of body and veins
'''
class Parasite():

    # Initialize Parasite object
    # Parameters:
    # sess_name: Name of the session for file-saving purposes
    # body_img_path: the path to the body image file
    # veins_img_path: the path to the veins image file
    # MicroImageClass: the MicroImage processing technique to use. I implemented 2: ScanLinesMicroImage, BitMapMicroImage
    def __init__(self, sess_name, body_img_path, veins_img_path, MicroImageClass):
        self.sess_name = sess_name
        self.mic_name = MicroImageClass.name
        self.body = MicroImageClass(body_img_path)
        self.veins = MicroImageClass(veins_img_path)
        self.veins_body_frac = self.calc_cancer()

    # Calculate the percentage of veins pixels within the body out of the whole body using the passed in 
    # MicroImage technique
    def calc_cancer(self):
        return self.body.calc_veins_perc(self.veins)

    # Determine whether the veins-to-body percentage is > than the cancer threshold (in our case 10%)
    def has_cancer(self):
        return self.veins_body_frac > cfg.CANCER_THRESH_PERC

    # Show a superimposed image of the loaded in body and veins image, using a 50% blend alpha
    def show_image(self):
        plt.imshow(Image.blend(self.body.raw, self.veins.raw, 0.5), cmap='gray')
        plt.show()

    # Save processed body data as a compressed numpy. Also print out compression rate
    def save_body_data(self):
        print("BODY DATA :")
        self.body.print_memory()
        self.body.save_processed_img(self.sess_name + "_body_" + self.mic_name)

    # Save processed veins data as a compressed numpy. Also print out compression rate
    def show_veins_data(self):
        print("VEINS DATA :")
        self.veins.print_memory()
        self.veins.save_processed_img(self.sess_name + "_veins_" + self.mic_name)

    # Save all the compressed data
    def save_data(self):
        self.save_body_data()
        self.show_veins_data()

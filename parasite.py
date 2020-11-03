from micro_image import ScanLinesMicroImage, BitMapMicroImage
import config as cfg
import os
import numpy as np


'''
Representation of a parasite's body and dye
'''
class Parasite():

    def __init__(self, sess_name, path_to_body):
        self.sess_name = sess_name
        self.body = ScanLinesMicroImage(path_to_body)
        # self.dye = BitMapMicroImage(path_to_dye)
        self.has_cancer = False

    def calc_cancer(self):
        return

    def has_cancer(self):
        return self.__has_cancer

    def show_image(self):
        return

    def save_body_data(self):
        self.body.print_memory()
        self.body.save_processed_img(self.sess_name + "_body")

    def save_dye_data(self):
        self.dye.print_memory()
        self.dye.save_processed_img(self.sess_name + "_dye")

    def save_data(self):
        self.save_body()
        self.save_dye()

if __name__ == "__main__":
    par1 = Parasite("lab0", os.path.join(cfg.COLLECTED_DIR, "med_sess_0.tiff"))
    par1.save_body_data()
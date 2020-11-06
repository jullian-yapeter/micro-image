import config as cfg
from micro_image_large import ScanLinesMicroImage, BitMapMicroImage
from parasite import Parasite
from simulate_data import Simulator
import os
import numpy as np


if __name__ == "__main__":

    session_name = "lab_sess"
    '''
    First, simulate some data using the Simulator class, upholding all rules given by Dragonfruit AI (i.e. body makes
    up >=25% of frame)
    '''
    # Simulator takes as argument:
    # session name, number of parasites to render, the size of the render, a list of size multipliers
    sim = Simulator(session_name, numSamples=2, size=(500, 500), resize_factors=[1, 2, 4])
    sim.show_all_frames() # Show the generated frames in which to draw the parasite
    sim.show_everything() # Show superimposed images of the parasite body and the corresponding veins
    sim.save_all_data() # Saves the rendered body and veins images as uncompressed TIFFs
    
    '''
    Next, Using the Parasite class, process and losslessly compress the body and veins image data and calculate whether
    the parasite has cancer; (Number of vein pixels within body makes up >-10% of the number of body pixels)
    '''
    # Parasite class takes an argument:
    # session name (for saving), path of raw body img, path of raw veins img, MicroImage processing technique to use
    # I implemented 2 techniques for processing BitMapMicroImage and ScanLinesMicroImage.
    par1 = Parasite(session_name+"_0",
                    os.path.join(cfg.COLLECTED_DIR, session_name + "_1_rf4_body.tiff"),
                    os.path.join(cfg.COLLECTED_DIR, session_name + "_1_rf4_veins.tiff"),
                    ScanLinesMicroImage)
    # Show the loaded images (body and veins) superimposed on top of each other
    par1.show_image()
    print("-----PAR 0-----")
    # Perform validation routines that ensure raw image = inv_process(process(raw_image))
    print("Body Process & Inverse Validity:", par1.body.validate_process())
    print("Veins Process & Inverse Validity:", par1.veins.validate_process())
    # Output the number of vein pixels within the body as a percentage of the total number of body pixels
    print("Veins to Body %:", par1.veins_body_frac * 100)
    # Output whether the current parasite has cancer
    print("Has cancer:", par1.has_cancer())
    # Save the processed data in compressed numpy arrays
    par1.save_data()

    '''
    Lastly, let's compare the compression rate to the )
    '''
    # Parasite class takes an argument:
    # session name (for saving), path of raw body img, path of raw veins img, MicroImage processing technique to use
    # I implemented 2 techniques for processing BitMapMicroImage and ScanLinesMicroImage.
    par2 = Parasite(session_name+"_1",
                    os.path.join(cfg.COLLECTED_DIR, session_name + "_1_rf4_body.tiff"),
                    os.path.join(cfg.COLLECTED_DIR, session_name + "_1_rf4_veins.tiff"),
                    BitMapMicroImage)
    # Show the loaded images (body and veins) superimposed on top of each other
    par2.show_image()
    print("-----PAR 1-----")
    # Perform validation routines that ensure raw image = inv_process(process(raw_image))
    print("Body Process & Inverse Validity:", par2.body.validate_process())
    print("Veins Process & Inverse Validity:", par2.veins.validate_process())
    # Output the number of vein pixels within the body as a percentage of the total number of body pixels
    print("Veins to Body %:", par2.veins_body_frac * 100)
    # Output whether the current parasite has cancer
    print("Has cancer:", par2.has_cancer())
    # Save the processed data in compressed numpy arrays
    par2.save_data()

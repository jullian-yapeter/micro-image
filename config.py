import os

'''
Directory configurations
'''
DATA_DIR = "data"
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
COLLECTED_DIR = os.path.join(DATA_DIR, "collected")
SPECIAL_COLLECTED_DIR = os.path.join(DATA_DIR, "special_collected")

'''
Data Information
'''
MAX_ROWS = 100000
MAX_COLS = 100000

'''
Data simulation configuration
'''
MIN_BODY_FRAME_PERC = 0.25
CANCER_THRESH_PERC = 0.10
SIM_CANCER_RATE = 0.001
BODY_RECURSION_DEPTH_LIMIT = 1000
VEIN_RECURSION_DEPTH_LIMIT = 400
NUM_BODY_RUNS = 3
NUM_VEIN_STRANDS = 3
BODY_THICKNESS_PERC = 0.1
VEIN_THICKNESS_PERC = BODY_THICKNESS_PERC * 0.1


'''
Image Processing metadata
'''
SCANLINES_CHECKBYTES = 179 # make sure to fit in uint8
BITMAP_CHECKBYTES = 179
SCANLINES_DTYPE = "uint16"
BITMAP_DTYPE = "uint8"
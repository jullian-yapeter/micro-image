import os

'''
Directory configurations
'''

DATA_DIR = "data"
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
COLLECTED_DIR = os.path.join(DATA_DIR, "collected")

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
RECURSION_DEPTH_LIMIT = 222

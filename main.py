from parasite import Parasite
import config as cfg
import os
import numpy as np


if __name__ == "__main__":
    par1 = Parasite(10, 10)
    par1.save_body_data()
    par1.save_dye_data()
    body = np.load(os.path.join(cfg.SAVE_DIR, "body.npy"))
    dye = np.load(os.path.join(cfg.SAVE_DIR, "dye.npy"))
    print(f"body: {body}")
    print(f"dye: {dye}")

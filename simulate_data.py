import config as cfg
import matplotlib.pyplot as plt
import numpy as np
from random import randint
import os
import sys

sys.setrecursionlimit(10**6)


class Simulator():

    def __init__(self, sessName, numSamples=1, size=(100, 100)):
        self.sessName = sessName
        self.frames = [Frame(size) for i in range(numSamples)]
        self.imgs = self._create_all_images()

    def show_all_frames(self):
        for frame in self.frames:
            frame.show_frame()

    def show_all_images(self):
        for img in self.imgs:
            plt.imshow(1-img, cmap='gray')
            plt.show()

    def save_all_images(self):
        for i, img in enumerate(self.imgs):
            path = os.path.join(cfg.COLLECTED_DIR, f"{self.sessName}_{i}.jpeg")
            plt.imsave(path, img, cmap='gray')

    def _create_all_images(self):
        return [self._create_image(frame) for frame in self.frames]

    def _create_image(self, frame):
        outer_frame, inner_frame = frame.frame_to_arrays()
        mid_pix = [round(inner_frame.shape[0] / 2), round(inner_frame.shape[1] / 2)]
        border_coords = self._create_border(inner_frame, mid_pix[1])
        if not self._is_valid_pix(inner_frame, border_coords, mid_pix[0], mid_pix[1]):
            print(border_coords[mid_pix[0]])
            print(mid_pix)
            print(inner_frame[mid_pix[0], mid_pix[1]])
        self._fill_body(inner_frame, border_coords, mid_pix[0], mid_pix[1])
        return frame.place_inner_into_outer(outer_frame, inner_frame)

    def _create_border(self, body_frame, mid_col):
        return [(mid_col - randint(1, round(body_frame.shape[1]/2)), mid_col + randint(1, round(body_frame.shape[1]/2)))
                for row in range(body_frame.shape[0])]

    def _is_valid_pix(self, body_frame, border_coords, row, col):
        return (row >= 0 and row < body_frame.shape[0]) and \
            (col >= 0 and col < body_frame.shape[1]) and \
            (col >= border_coords[row][0] and col <= border_coords[row][1]) and \
            (body_frame[row, col] != 1)

    def _fill_body(self, body_frame, border_coords, row, col):
        if self._is_valid_pix(body_frame, border_coords, row, col):
            body_frame[row, col] = 1
            for i in range(-1, 2, 1):
                for j in range(-1, 2, 1):
                    if (not(i == 0 and j == 0)):
                        self._fill_body(body_frame, border_coords, row + i, col + j)


class Frame():

    def __init__(self, size=(10, 10)):
        self.outerf_dim = size
        self.innerf_dim = self._set_innerf()
        self.anchor = self._set_anchor()

    def _set_innerf(self):
        min_width = round(self.outerf_dim[1] * cfg.MIN_BODY_FRAME_PERC * 2)
        min_height = round(self.outerf_dim[0] * cfg.MIN_BODY_FRAME_PERC * 2)
        width = randint(min_width, self.outerf_dim[1])
        height = randint(min_height, self.outerf_dim[0])
        return [height, width]

    def _set_anchor(self):
        max_x = self.outerf_dim[1] - self.innerf_dim[1]
        max_y = self.outerf_dim[0] - self.innerf_dim[0]
        anchor_x = randint(0, max_x)
        anchor_y = randint(0, max_y)
        return [anchor_y, anchor_x]

    def innerf_area_perc(self):
        return (self.innerf_dim[0] * self.innerf_dim[1]) / (self.outerf_dim[0] * self.outerf_dim[1]) * 100.0

    def frame_to_arrays(self):
        outer_frame = np.zeros(self.outerf_dim)
        inner_frame = np.zeros(self.innerf_dim)
        return outer_frame.copy(), inner_frame.copy()

    def place_inner_into_outer(self, outer_frame, inner_frame):
        res = np.copy(outer_frame)
        res[self.anchor[0]:self.anchor[0]+inner_frame.shape[0],
            self.anchor[1]:self.anchor[1]+inner_frame.shape[1]] = inner_frame
        return res

    def show_frame(self):
        outer_frame, inner_frame = self.frame_to_arrays()
        outer_frame += 1
        comb_frame = self.place_inner_into_outer(outer_frame, inner_frame)
        plt.imshow(comb_frame)
        plt.title(str("{:.2f}".format(self.innerf_area_perc())))
        plt.show()


if __name__ == "__main__":
    sim = Simulator("raw_sess", numSamples=10)
    sim.show_all_images()
    sim.save_all_images()

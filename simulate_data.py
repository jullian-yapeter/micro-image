import config as cfg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from random import randint, choice
import os
import sys

sys.setrecursionlimit(10**6)


class Simulator():

    def __init__(self, sess_name, numSamples=1, size=(100, 100), im_save_type="png"):
        self.sess_name = sess_name
        self.im_save_type = im_save_type
        if size[0] < cfg.MAX_ROWS and size[1] < cfg.MAX_COLS:
            self.frames = [Frame(size) for i in range(numSamples)]
            self.bodies = self._create_all_bodies(num_runs=cfg.NUM_BODY_RUNS, thickness=cfg.BODY_THICKNESS)
            self.veins = self._create_all_veins(num_strands=cfg.NUM_VEIN_STRANDS, thickness=cfg.VEIN_THICKNESS)
        else:
            raise ValueError("Passed in size is too large")

    def show_everything(self):
        for bd, vs in zip(self.bodies, self.veins):
            plt.imshow(255-np.minimum(bd//5 + vs//3, 255), cmap='gray')
            plt.show()

    def show_all_frames(self):
        for frame in self.frames:
            frame.show_frame()

    def show_all_bodies(self):
        for img in self.bodies:
            plt.imshow(255-img, cmap='gray')
            plt.show()

    def show_all_veins(self):
        for vs in self.veins:
            plt.imshow(255-vs, cmap='gray')
            plt.show()

    def save_all_bodies(self):
        for i, img in enumerate(self.bodies):
            path = os.path.join(cfg.COLLECTED_DIR, f"{self.sess_name}_{i}_body.{self.im_save_type}")
            Image.fromarray(255-img).save(path)

    def save_all_veins(self):
        for i, img in enumerate(self.veins):
            path = os.path.join(cfg.COLLECTED_DIR, f"{self.sess_name}_{i}_veins.{self.im_save_type}")
            Image.fromarray(255-img).save(path)

    def _create_all_bodies(self, num_runs=3, thickness=40):
        return [self._create_body(frame, num_runs=num_runs, thickness=thickness) for frame in self.frames]

    def _create_body(self, frame, num_runs=3, thickness=40):
        outer_frame, inner_frame = frame.frame_to_arrays()
        mid_pix = self._get_mid_pix(inner_frame)
        for i in range(num_runs):
            self._random_stroke_recur(inner_frame, mid_pix[0], mid_pix[1], 0, cfg.BODY_RECURSION_DEPTH_LIMIT, thickness=thickness)
        return frame.place_inner_into_outer(outer_frame, inner_frame).astype(np.uint8)

    # def _create_body(self, frame):
    #     outer_frame, inner_frame = frame.frame_to_arrays()
    #     mid_pix = self._get_mid_pix(inner_frame)
    #     border_coords = self._create_border(inner_frame, mid_pix[1])
    #     self._fill_body(inner_frame, border_coords)
    #     return frame.place_inner_into_outer(outer_frame, inner_frame).astype(np.uint8)

    def _create_border(self, body_frame, mid_col):
        return [(mid_col - randint(1, round(body_frame.shape[1]/2)), mid_col + randint(1, round(body_frame.shape[1]/2)))
                for row in range(body_frame.shape[0])]

    def _fill_body(self, body_frame, border_coords):
        for row in range(body_frame.shape[0]):
            body_frame[row, border_coords[row][0]: border_coords[row][1] + 1] = 255

    def _create_all_veins(self, num_strands=2, thickness=3):
        return [self._create_veins(frame, num_strands=num_strands) for frame in self.frames]

    def _create_veins(self, frame, num_strands=2, thickness=3):
        outer_frame, inner_frame = frame.frame_to_arrays()
        mid_pix = [sum(x) for x in zip(frame.anchor, self._get_mid_pix(inner_frame))]
        for i in range(num_strands):
            self._random_stroke_recur(outer_frame, mid_pix[0], mid_pix[1], 0, cfg.VEIN_RECURSION_DEPTH_LIMIT, v_dir=1, thickness=thickness)
            self._random_stroke_recur(outer_frame, mid_pix[0], mid_pix[1], 0, cfg.VEIN_RECURSION_DEPTH_LIMIT, v_dir=-1, thickness=thickness)
            self._random_stroke_recur(outer_frame, mid_pix[0], mid_pix[1], 0, cfg.VEIN_RECURSION_DEPTH_LIMIT, h_dir=1, thickness=thickness)
            self._random_stroke_recur(outer_frame, mid_pix[0], mid_pix[1], 0, cfg.VEIN_RECURSION_DEPTH_LIMIT, h_dir=-1, thickness=thickness)
        return outer_frame.astype(np.uint8)

    def _random_stroke_recur(self, frame, row, col, r_depth, lim_depth, v_dir=None, h_dir=None, thickness=3):
        def _is_valid_pix(frame, row, col):
            return (row >= 0 and row < frame.shape[0]) and \
                (col >= 0 and col < frame.shape[1]) and \
                r_depth < lim_depth
        if _is_valid_pix(frame, row, col):
            self._square_stamp(frame, row, col, thickness)
            if h_dir is None and v_dir is not None:
                dir_x, dir_y = choice((0, v_dir)), choice((-1, 1))
            elif v_dir is None and h_dir is not None:
                dir_x, dir_y = choice((-1, 1)), choice((0, h_dir))
            else:
                dir_x, dir_y = choice((-1, 0, 1)), choice((-1, 0, 1))
            self._random_stroke_recur(frame, round(row + ((thickness + 1)/ 2) * dir_x),
                    round(col + ((thickness + 1)/ 2) * dir_y), r_depth+1, lim_depth, v_dir=v_dir, h_dir=h_dir, thickness=thickness)

    def _square_stamp(self, frame, row, col, dim):
        def _is_valid_pix(frame, row, col):
            return (row >= 0 and row < frame.shape[0]) and \
                (col >= 0 and col < frame.shape[1])
        for i in range(-int(dim/2), int(dim/2)):
            for j in range(-int(dim/2), int(dim/2)):
                if _is_valid_pix(frame, row + i, col + j):
                    frame[row + i, col + j] = 255

    def _get_mid_pix(self, frame):
        return [round(frame.shape[0] / 2), round(frame.shape[1] / 2)]

    ## Recursive implementation of _fill_body
    # def _fill_body_recur(self, body_frame, border_coords, row, col):
    #     def _is_valid_pix(body_frame, border_coords, row, col):
    #         return (row >= 0 and row < body_frame.shape[0]) and \
    #             (col >= 0 and col < body_frame.shape[1]) and \
    #             (col >= border_coords[row][0] and col <= border_coords[row][1]) and \
    #             (body_frame[row, col] != 1)
    #     if _is_valid_pix(body_frame, border_coords, row, col):
    #         body_frame[row, col] = 1
    #         for i in range(-1, 2, 1):
    #             for j in range(-1, 2, 1):
    #                 if (not(i == 0 and j == 0)):
    #                     self._fill_body(body_frame, border_coords, row + i, col + j)


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
    # sim = Simulator("big_sess", numSamples=5, size=(5000, 5000))
    # sim.show_all_bodies()
    # sim.save_all_bodies()
    # sim = Simulator("med_sess", numSamples=5, size=(1000, 1000))
    # sim.show_all_bodies()
    # sim.save_all_bodies()
    # sim = Simulator("small_sess", numSamples=5, size=(100, 100))
    # sim.show_all_bodies()
    # sim.save_all_bodies()
    sim = Simulator("small_sess", numSamples=1, size=(1000, 1000))
    sim.show_everything()
    # sim.save_all_bodies()
    # sim.save_all_veins()


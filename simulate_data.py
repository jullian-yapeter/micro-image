import config as cfg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from random import randint, choice
from skimage.transform import resize
import os
import sys

sys.setrecursionlimit(10**6)

'''
Simulator class to produce images of Parasites' bodies and veins, and save them to TIFF files.
'''
class Simulator():
    # Initialize Simulator class
    # Parameters:
    # sess_name: The name of the session for file-saving purposes
    # numSamples: The number of Body-Veins pairs to render
    # size: The size of the image to render
    # im_save_type: The image format to save with, default = TIFF
    # resize_factors: List of resizing factors to apply on the rendered images, require at least 1 element in list
    def __init__(self, sess_name, numSamples=1, size=(100, 100), im_save_type="tiff", resize_factors=[1]):
        self.sess_name = sess_name
        self.im_save_type = im_save_type
        if size[0] < cfg.MAX_ROWS and size[1] < cfg.MAX_COLS:
            self.frames = [Frame(size) for i in range(numSamples)]
            self.bodies = self._create_all_bodies(num_runs=cfg.NUM_BODY_RUNS, thickness=int(size[0] * cfg.BODY_THICKNESS_PERC))
            self.veins = self._create_all_veins(num_strands=cfg.NUM_VEIN_STRANDS, thickness=int(size[0] * cfg.VEIN_THICKNESS_PERC))
            self.size = size
            self.resize_factors = resize_factors
        else:
            raise ValueError("Passed in size is too large")

    # Show superimposed images of body-vein pairs
    def show_everything(self):
        for bd, vs in zip(self.bodies, self.veins):
            plt.imshow(255-np.minimum(bd//5 + vs//3, 255), cmap='gray')
            plt.show()

    # Show the Frames in which the body and veins pixels are drawn onto (Frame class objects)
    def show_all_frames(self):
        for frame in self.frames:
            frame.show_frame()

    # Show all the rendered images of parasite bodies
    def show_all_bodies(self):
        for img in self.bodies:
            plt.imshow(255-img, cmap='gray')
            plt.show()

    # # Show all the rendered images of parasite veins
    def show_all_veins(self):
        for vs in self.veins:
            plt.imshow(255-vs, cmap='gray')
            plt.show()

    # Save all the rendered images of bodies and veins
    def save_all_data(self):
        self.save_all_bodies()
        self.save_all_veins

    # Save only the images of all the rendered body images
    # The filename will be {session name}_{sample number}_rf{resize factor}_body.{file type}
    # Resizing happens using interpolation with NEAREST pixel sampling
    def save_all_bodies(self):
        for rf in self.resize_factors:
            for i, img in enumerate(self.bodies):
                path = os.path.join(cfg.COLLECTED_DIR, f"{self.sess_name}_{i}_rf{rf}_body.{self.im_save_type}")
                Image.fromarray(255-img).resize((self.size[0] * rf, self.size[1] * rf),
                                                resample=Image.NEAREST).save(path)

    # Save only the images of all the rendered veins images
    # The filename will be {session name}_{sample number}_rf{resize factor}_veins.{file type}
    # Resizing happens using interpolation with NEAREST pixel sampling
    def save_all_veins(self):
        for rf in self.resize_factors:
            for i, img in enumerate(self.veins):
                path = os.path.join(cfg.COLLECTED_DIR, f"{self.sess_name}_{i}_rf{rf}_veins.{self.im_save_type}")
                Image.fromarray(255-img).resize((self.size[0] * rf, self.size[1] * rf),
                                                resample=Image.NEAREST).save(path)

    # Create a list of body images
    # Parameters:
    # num_runs: number of recursive random brush strokes to run to draw one body image
    # thickness: width of square brush
    def _create_all_bodies(self, num_runs=3, thickness=40):
        return [self._create_body(frame, num_runs=num_runs, thickness=thickness) for frame in self.frames]

    # Create body image
    # Parameters:
    # frame: the frame in which to draw the body image
    # num_runs: number of recursive random brush strokes to run to draw one body image
    # thickness: width of square brush
    def _create_body(self, frame, num_runs=3, thickness=40):
        outer_frame, inner_frame = frame.frame_to_arrays()
        drawing_canvas = outer_frame.copy()
        mid_pix = self._get_mid_pix(drawing_canvas)
        for i in range(num_runs):
            # Perform recursive drawing
            self._random_stroke_recur(drawing_canvas, mid_pix[0], mid_pix[1], 0,
                                      cfg.BODY_RECURSION_DEPTH_LIMIT, thickness=thickness)
        # Resize the body drawing to zoom fit exactly the generate inner frame (Ensure body is 25% of frame)
        drawing_canvas = resize(self._trim_empty_border(drawing_canvas), inner_frame.shape)
        return frame.place_inner_into_outer(outer_frame, drawing_canvas).astype(np.uint8)

    # helper function to trim off the empty rows and columns untouched by the recursive drawing brush
    # Parameters:
    # frame: the image to trim empty borders off of
    def _trim_empty_border(self, img):
        rows, cols = np.any(img, axis=1), np.any(img, axis=0)
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        return img[ymin:ymax+1, xmin:xmax+1]

    # This is used in the non-recursive scanline version of drawing parasites. draws random scanlines around middle
    # pixel.
    # Parameters:
    # body_frame: the frame in which to draw the body pixels
    # mid_col: the middle pixel, to ensure the scan lines of the body create a contiguous shape
    def _create_border(self, body_frame, mid_col):
        return [(mid_col - randint(1, round(body_frame.shape[1]/2)), mid_col + randint(1, round(body_frame.shape[1]/2)))
                for row in range(body_frame.shape[0])]

    # Fills up between the created borders (_create_border) iteratively
    # Parameters:
    # body_frame: the frame in which to draw the body pixels
    # border_coords: the created border coords (to fill between)
    def _fill_body(self, body_frame, border_coords):
        for row in range(body_frame.shape[0]):
            body_frame[row, border_coords[row][0]: border_coords[row][1] + 1] = 255

    # Create a list of veins images
    # Parameters:
    # num_strands: number of vein strands extending towards each of the 4 directions (up, down, left, right)
    # thickness: width of square brush
    def _create_all_veins(self, num_strands=2, thickness=3):
        return [self._create_veins(frame, num_strands=num_strands, thickness=thickness) for frame in self.frames]

    # Create veins image
    # Parameters:
    # frame: the frame in which to draw the veins image
    # num_strands: number of vein strands extending towards each of the 4 directions (up, down, left, right)
    # thickness: width of square brush
    def _create_veins(self, frame, num_strands=2, thickness=3):
        outer_frame, inner_frame = frame.frame_to_arrays()
        mid_pix = [sum(x) for x in zip(frame.anchor, self._get_mid_pix(inner_frame))]
        for i in range(num_strands):
            for (v, h) in [(1, None), (-1, None), (None, 1), (None, -1)]:
                # perform recursive drawing
                self._random_stroke_recur(outer_frame, mid_pix[0], mid_pix[1], 0, cfg.VEIN_RECURSION_DEPTH_LIMIT,
                                          v_dir=v, h_dir=h, thickness=thickness)
        return outer_frame.astype(np.uint8)

    # Performs random drawing on a given frame. Draws body and veins recursively
    # Parameters:
    # frame: the frame in which to draw
    # row, col: the row and column of the origin of the drawing
    # r_deth: current recursive depth
    # lim_depth: recursive depth limit
    # v_dir: either None, 1 (extend drawing upwards), or -1 (extend drawing downwards)
    # h_dir: either None, 1 (extend drawing right), or -1 (extend drawing left)
    # thickness: width of square brush
    def _random_stroke_recur(self, frame, row, col, r_depth, lim_depth, v_dir=None, h_dir=None, thickness=3):
        # helper function to check if pixel is valid to run a recursive call on
        def _is_valid_pix(frame, row, col):
            return (row >= 0 and row < frame.shape[0]) and \
                (col >= 0 and col < frame.shape[1]) and \
                r_depth < lim_depth
        if _is_valid_pix(frame, row, col):
            self._square_stamp(frame, row, col, thickness)
            if h_dir is None and v_dir is not None:
                dir_x, dir_y = choice((0, v_dir)), choice((-1, 1)) # Force a more vertical path
            elif v_dir is None and h_dir is not None:
                dir_x, dir_y = choice((-1, 1)), choice((0, h_dir)) # Force a more horizontal path
            else:
                dir_x, dir_y = choice((-1, 0, 1)), choice((-1, 0, 1)) # Not force any direction
            self._random_stroke_recur(frame, round(row + ((thickness + 1)/ 2) * dir_x),
                                      round(col + ((thickness + 1)/ 2) * dir_y), r_depth+1, lim_depth,
                                      v_dir=v_dir, h_dir=h_dir, thickness=thickness)

    # Square brush dot
    # Parameters:
    # frame: the frame in which to draw
    # row, col: the middle of the dot
    # dim: the dimension of the square brush
    def _square_stamp(self, frame, row, col, dim):
        def _is_valid_pix(frame, row, col):
            return (row >= 0 and row < frame.shape[0]) and \
                (col >= 0 and col < frame.shape[1])
        for i in range(-int(dim/2), int(dim/2)):
            for j in range(-int(dim/2), int(dim/2)):
                if _is_valid_pix(frame, row + i, col + j):
                    frame[row + i, col + j] = 255

    # Helper function to get the middle pixel row and column number of a given frame
    # Parameters:
    # frame: the frame to get middle pixel row and col from
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
    #                     self._fill_body_recur(body_frame, border_coords, row + i, col + j)

'''
Frame class is used to randomly generate valid outer and inner empty frames in which to draw parasites.
The inner frame will contain the body of the parasite and the outer frame will contain the veins
'''
class Frame():

    # Initialize Frame object
    # Parameters:
    # size: the size of the outer frame to generate
    def __init__(self, size=(10, 10)):
        self.outerf_dim = size
        self.innerf_dim = self._set_innerf()
        self.anchor = self._set_anchor()

    # Determine random inner frame dimensions, ensuring the body takes up 25% of the frame
    def _set_innerf(self):
        min_width = round(self.outerf_dim[1] * cfg.MIN_BODY_FRAME_PERC * 2)
        min_height = round(self.outerf_dim[0] * cfg.MIN_BODY_FRAME_PERC * 2)
        width = randint(min_width, self.outerf_dim[1])
        height = randint(min_height, self.outerf_dim[0])
        return [height, width]

    # Determine random but valid anchor (top left pixel location) for the inner frame to be placed into the outer frame
    def _set_anchor(self):
        max_x = self.outerf_dim[1] - self.innerf_dim[1]
        max_y = self.outerf_dim[0] - self.innerf_dim[0]
        anchor_x = randint(0, max_x)
        anchor_y = randint(0, max_y)
        return [anchor_y, anchor_x]

    # Calculate the area percentage of the inner frame as it relates to the outer frame
    def innerf_area_perc(self):
        return (self.innerf_dim[0] * self.innerf_dim[1]) / (self.outerf_dim[0] * self.outerf_dim[1]) * 100.0

    # output the generated frames as numpy arrays
    def frame_to_arrays(self):
        outer_frame = np.zeros(self.outerf_dim)
        inner_frame = np.zeros(self.innerf_dim)
        return outer_frame.copy(), inner_frame.copy() # defensive copy

    # helper function used to place an inner frame into an outer frame
    # Parameters: 
    # outer_frame: the outer frame
    # inner_frame: the inner frame
    def place_inner_into_outer(self, outer_frame, inner_frame):
        res = np.copy(outer_frame)
        res[self.anchor[0]:self.anchor[0]+inner_frame.shape[0],
            self.anchor[1]:self.anchor[1]+inner_frame.shape[1]] = inner_frame
        return res

    # Shows the generated frames on which to draw the parasites. Shows inner frame area as a percentage of 
    # the outer frame area.
    def show_frame(self):
        outer_frame, inner_frame = self.frame_to_arrays()
        outer_frame += 1
        comb_frame = self.place_inner_into_outer(outer_frame, inner_frame)
        plt.imshow(comb_frame)
        plt.title(str("{:.2f}".format(self.innerf_area_perc())))
        plt.show()


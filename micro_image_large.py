import config as cfg
import base64
from io import BytesIO  
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image, ImageChops
from sys import getsizeof


'''
MicroImageLarge class handles the loading, processing, and process validation of parasite images
'''
class MicroImageLarge():

    # Initialize MicroImageLarge object
    # Parameters:
    # Path: the path to the image file to be processed
    def __init__(self, path):
        self.raw_size = os.path.getsize(path)
        self.raw = self._read_img(path)
        self.processed = self._process()

    # Reads image file, currently uses Pillow
    # Parameters:
    # Path: the path to the image file to be processed
    def _read_img(self, path):
        return Image.open(path)

    # Helper function to convert a binary numpy (1 for positive pixel, 0 for background) to a 0 255 Pillow image
    # Parameters:
    # bin_npy: binary numpy (1 for positive pixel, 0 for background)
    def _bin_npy_to_raw(self, bin_npy):
        return Image.fromarray((1-bin_npy.astype(np.uint8))*255)

    # Create an 8-bit friendly representation of an image size 
    # E.g. 1080 * 950 => 4,1,0,8,0,3,9,5,0
    # rows, cols: number of rows and columns of the image
    def _make_shape_repr(self, rows, cols):
        rows_ls = [int(c) for c in str(rows)]
        cols_ls = [int(c) for c in str(cols)]
        return [len(rows_ls)] + [len(cols_ls)] + rows_ls  + cols_ls

    # inverse of _make_shape_repr
    # E.g. 4,1,0,8,0,3,9,5,0 => 1080 * 950 
    def _ret_shape_from_repr(self, shape_repr):
        data_start_idx = shape_repr[0] + shape_repr[1] + 2
        num_rows = int("".join(map(str, shape_repr[2:2 + shape_repr[0]])))
        num_cols = int("".join(map(str, shape_repr[2 + shape_repr[0]:2 + shape_repr[0] + shape_repr[1]])))
        return data_start_idx, num_rows, num_cols

    # the processing routine packs a header into the numpy packet to ensure robustness (check bytes and image size)
    # Parameters:
    # processed: the processed image
    def _ret_header(self, processed):
        check_byte = processed[0]
        data_start_idx, num_rows, num_cols = self._ret_shape_from_repr(processed[1:])
        return check_byte, data_start_idx + 1, num_rows, num_cols
    
    # Processing routine to compress parasite images to smaller numpy arrays
    def _process(self):
        raise NotImplementedError

    # Inverse of _process, turns a compressed numpy array to a Pillow image
    # Parameters:
    # processed_img: result of _process()
    def _inverse_process(self, processed_img):
        raise NotImplementedError

    # Performs a validation sequence that checks for differences between the raw Pillow
    def validate_process(self):
        return (ImageChops.difference(self.raw, self._inverse_process(self.processed)).getbbox()) is None

    # Shows the raw image
    def show_raw_img(self):
        plt.imshow(self.raw, cmap='gray')
        plt.show()

    # Shows the inversed(processed(raw)) image
    def show_inversed_img(self):
        plt.imshow(self._inverse_process(self.processed), cmap='gray')
        plt.show()

    # saves the processed image
    # Parameters:
    # filename: the filename with which to save the processed image
    def save_processed_img(self, filename):
        raise NotImplementedError

    # print the memory usage of the raw and processed images, as well as the compression rate
    def print_memory(self):
        raise NotImplementedError

    # calculate the percentage of veins pixels within the body as it relates to the whole body
    def calc_veins_perc(self, veins_of_this_body):
        return NotImplementedError

'''
ScanLinesMicroImage class handles the loading, processing, and process validation of parasite images.
It is a subclass of MicroImageLarge class.
'''
class ScanLinesMicroImage(MicroImageLarge):

    name = "scanlines" # Name of MicroImageLarge subclass
    dtype = cfg.SCANLINES_DTYPE # Set dtype being used by this MicroImageLarge subclass (currently "uint16")

    def __init__(self, path):
        super().__init__(path)
        
    # helper function to convert a pixel index to row and col number
    # E.g for a 10x10 image, pixel index 23 will be row=2 col=3
    def _pix_to_rc(self, pix, numCols):
        return int(pix // numCols), int(pix % numCols)

    # Process the image using the ScanLines method
    # Taking a scan line approach, record the number of pixels before a pixel value switches from either 0 to 255 or
    # 255 to 0. Even handles cases where the number of pixels before the next switch is larger than what can fit in 
    # the dtype.
    def _process(self):
        cols, rows = self.raw.size
        res = [cfg.SCANLINES_CHECKBYTES] + self._make_shape_repr(rows, cols) # Pack check byte and image size
        curr = 255
        curr_count = 0
        first_entry = True
        for pix, val in enumerate(self.raw.getdata()):
            if val != curr: # value switch occurred
                if (first_entry): # On first entry, save a lot of memory by storing rows and cols instead of num pixels
                    r, c = self._pix_to_rc(pix, cols)
                    res = res + self._make_shape_repr(r, c)
                    first_entry = False
                else:
                    res.append(pix-curr_count)
                curr = val
                curr_count = pix
            elif (not first_entry) and ((pix-curr_count) == np.iinfo(self.dtype).max): # max out dtype before a switch
                res.append(0) # flag it with a zero
                curr_count = pix
        return np.array(res, dtype=self.dtype)

    # Inverse of _process, turns a compressed numpy array to a Pillow image
    # Parameters:
    # processed_img: result of _process()
    def _inverse_process(self, processed_img):
        check_byte, data_start_idx, num_rows, num_cols = self._ret_header(processed_img) # unpack header
        if processed_img[0] != cfg.SCANLINES_CHECKBYTES: # Ensure correct checbytes
            raise ValueError("Check bytes for scanlines inverse process are incorrect")
            return None
        start_idx_so_far, rows_so_far, cols_so_far = self._ret_shape_from_repr(processed_img[data_start_idx:])
        brush = 1 # value with which to draw the scan line
        pix_so_far = rows_so_far * num_cols + cols_so_far
        res = np.zeros((1, num_rows * num_cols), dtype=self.dtype)
        for brush_switch in processed_img[data_start_idx + start_idx_so_far:]:
            if brush_switch == 0: # in the case where a dtype max out occurred
                res[0, pix_so_far : pix_so_far + np.iinfo(self.dtype).max] = brush
                pix_so_far += np.iinfo(self.dtype).max
            else:
                res[0, pix_so_far : pix_so_far + brush_switch] = brush
                pix_so_far += brush_switch
                brush = 1 - brush
        res = res.reshape(num_rows, num_cols) # res is now a binary numpy (COULD BE USEFUL FOR FUTURE)
        res_img = self._bin_npy_to_raw(res) # convert binary numpy to Pillow image
        return res_img

    # saves the processed image
    # Parameters:
    # filename: the filename with which to save the processed image
    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.npy")
        np.save(path, self.processed)

    # print the memory usage of the raw and processed images, as well as the compression rate
    def print_memory(self):
        print("---RAW---")
        print(f"total size of raw data (bytes): {self.raw_size}")
        print("")

        print("---PROCESSED---")
        print(f"num elements : {self.processed.size}")
        print(f"size of each element (bytes): {self.processed.itemsize}")
        print(f"total size of processed data (bytes): {self.processed.nbytes}")
        print(f"Percentage of original size (%): {self.processed.nbytes / self.raw_size}")
        print("")

    # calculate the percentage of veins pixels within the body as it relates to the whole body
    # Use ScanLines processed body image and Pillow image generator functionality of veins image
    def calc_veins_perc(self, veins_of_this_body):
        check_byte, data_start_idx, num_rows, num_cols = self._ret_header(self.processed)
        start_idx_so_far, rows_so_far, cols_so_far = self._ret_shape_from_repr(self.processed[data_start_idx:])
        brush = 1 # value of the scan line
        pix_so_far = rows_so_far * num_cols + cols_so_far
        valid_vein = 0 # Number of vein pixels that are within the body of the parasite
        num_body_pix = 0 # Keep track of number of body pixels
        v = veins_of_this_body.raw.getdata()
        temp = []
        for brush_switch in self.processed[data_start_idx + start_idx_so_far:]:
            if brush_switch == 0:
                if brush==1:
                    temp = np.array([v[pix_so_far + i] for i in range(np.iinfo(self.dtype).max)])
                    valid_vein += np.sum((255-temp)//255)
                    temp = []
                    num_body_pix += np.iinfo(self.dtype).max
                pix_so_far += np.iinfo(self.dtype).max
            else:
                if brush==1:
                    temp = np.array([v[pix_so_far + i] for i in range(brush_switch)])
                    valid_vein += np.sum((255-temp)//255)
                    temp = []
                    num_body_pix += brush_switch
                pix_so_far += brush_switch
                brush = 1 - brush
        return valid_vein / num_body_pix # return fraction of vein-in-body to body

'''
BitMapMicroImage class handles the loading, processing, and process validation of parasite images.
It is a subclass of MicroImageLarge class.
'''
class BitMapMicroImage(MicroImageLarge):

    name = "bitmap" # Name of MicroImageLarge subclass
    dtype = cfg.BITMAP_DTYPE # Set dtype being used by this MicroImageLarge subclass (currently "uint8")

    def __init__(self, path):
        super().__init__(path)

    # Process the image using the BitMap method
    # Converts the image into a series of bits, 1 to represent a positive pixel and 0 to represent a background pixel.
    # Also packs in a header of check byte and size of original image
    def _process(self):
        cols, rows = self.raw.size
        res = [cfg.BITMAP_CHECKBYTES] + self._make_shape_repr(rows, cols)
        buffer = []
        for pix, val in enumerate(self.raw.getdata()):
            buffer.append(1-val//255)
            if len(buffer) % 8 == 0: # for every packet of 8 pixels
                bin_int = int("".join(map(str, buffer)), 2) # convert the base 2 value to base 10
                res.append(bin_int)
                buffer = []
        return np.array(res, dtype=self.dtype)

    # Inverse of _process, turns a compressed numpy array to a Pillow image
    # Parameters:
    # processed_img: result of _process()
    def _inverse_process(self, processed_img):
        check_byte, data_start_idx, num_rows, num_cols = self._ret_header(processed_img)
        if check_byte != cfg.BITMAP_CHECKBYTES:
            raise ValueError("Check bytes for bitmap inverse process are incorrect")
            return None
        bin_npy_1d = []
        for pix, val in enumerate(self.processed[data_start_idx:]):
            a = self._cvt_b10_b2(val) # convert each base 10 int to base 2
            bin_npy_1d += a 
        bin_npy = np.array(bin_npy_1d, dtype=cfg.BITMAP_DTYPE).reshape(num_rows, num_cols)
        img = self._bin_npy_to_raw(bin_npy) # convert numpy to Pillow image
        return img

    # Helper function to convert base 10 number to an array of 1s and 0s (assumes uint8)
    def _cvt_b10_b2(self, b10):
        if b10 == 0:
            return [0] * 8
        b2 = [int(char) for char in bin(int(b10))[2:]]
        return [0] * (8 - len(b2)) + b2
    
    # saves the processed image
    # Parameters:
    # filename: the filename with which to save the processed image
    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.npy")
        np.save(path, self.processed)

    # print the memory usage of the raw and processed images, as well as the compression rate
    def print_memory(self):
        print("---RAW---")
        print(f"total size of raw data (bytes): {self.raw_size}")
        print("")

        print("---PROCESSED---")
        print(f"num elements : {self.processed.size}")
        print(f"size of each element (bytes): {self.processed.itemsize}")
        print(f"total size of processed data (bytes): {self.processed.nbytes}")
        print(f"Percentage of original size (%): {self.processed.nbytes / self.raw_size}")
        print("")

    # calculate the percentage of veins pixels within the body as it relates to the whole body
    # Use BitMap processed image of body and and BitMap processed image of veins
    def calc_veins_perc(self, veins_of_this_body):
        check_byte, data_start_idx, num_rows, num_cols = self._ret_header(self.processed)
        valid_vein = 0
        num_body_pix = 0
        cols, rows = self.raw.size
        for body_pix, vein_pix in zip(self.processed[data_start_idx:], veins_of_this_body.processed[data_start_idx:]):
            valid_vein += sum([int(c) for c in bin(body_pix & vein_pix)[2:]])
            num_body_pix += sum([int(c) for c in bin(body_pix)[2:]])
        return valid_vein / num_body_pix

# Auxiliary class to show how this framework can be extended
class Base64MicroImage(MicroImageLarge):

    def __init__(self, path):
        super().__init__(path)

    def _process(self):
        buffer = BytesIO()
        self.raw.save(buffer, format="png")
        return base64.b64encode(buffer.getvalue())

    def _inverse_process(self, processed_img):
        img_bytes = base64.b64decode(processed_img)
        buf = BytesIO(img_bytes)
        img = Image.open(buf)
        return img

    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.out")
        with open(path, "wb") as outfile: 
            outfile.write(self.processed)

    def print_memory(self):
        print("---RAW---")
        print(f"total size of raw data (bytes): {self.raw_size}")
        print("")

        print("---PROCESSED---")
        print(f"total size of processed data (bytes): {getsizeof(self.processed)}")
        print(f"Percentage of original size (%): {getsizeof(self.processed) / self.raw_size}")
        print("")

    def calc_veins_perc(self, veins_of_this_body):
        return NotImplementedError

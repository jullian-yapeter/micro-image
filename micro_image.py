import config as cfg
import base64
from io import BytesIO  
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
from sys import getsizeof

'''
Refer to micro_image_large.py for code documentation
'''

'''
Image level data and methods
'''
class MicroImage():

    def __init__(self, path):
        self.raw_size = os.path.getsize(path)
        self.raw = self._read_img(path)
        self.binary_npy = self._raw_to_bin_npy(self.raw) # 1 for subject and 0 for background
        print(self.binary_npy.sum())
        self.processed = self._process()

    def _read_img(self, path):
        return Image.open(path)

    def _raw_to_bin_npy(self, raw):
        return ((255-np.asarray(raw)) / 255).astype(np.uint8)

    def _bin_npy_to_raw(self, bin_npy):
        return Image.fromarray((1-bin_npy.astype(np.uint8))*255)

    def _make_shape_repr(self, rows, cols):
        rows_ls = [int(c) for c in str(rows)]
        cols_ls = [int(c) for c in str(cols)]
        return [len(rows_ls)] + [len(cols_ls)] + rows_ls  + cols_ls

    def _ret_shape_from_repr(self, shape_repr):
        data_start_idx = shape_repr[0] + shape_repr[1] + 2
        num_rows = int("".join(map(str, shape_repr[2:2 + shape_repr[0]])))
        num_cols = int("".join(map(str, shape_repr[2 + shape_repr[0]:2 + shape_repr[0] + shape_repr[1]])))
        return data_start_idx, num_rows, num_cols

    def _ret_header(self, processed):
        check_byte = processed[0]
        data_start_idx, num_rows, num_cols = self._ret_shape_from_repr(processed[1:])
        return check_byte, data_start_idx + 1, num_rows, num_cols
        
    def _process(self):
        raise NotImplementedError

    def _inverse_process(self, processed_img):
        raise NotImplementedError

    def validate_process(self):
        return np.array_equal(self.binary_npy, self._raw_to_bin_npy(self._inverse_process(self.processed)))

    def show_raw_img(self):
        plt.imshow(self.raw, cmap='gray')
        plt.show()

    def show_binary_img(self):
        plt.imshow((1-self.binary_npy)*255, cmap='gray')
        plt.show()

    def save_processed_img(self, filename):
        raise NotImplementedError

    def print_memory(self):
        raise NotImplementedError

    def calc_veins_perc(self, veins_of_this_body):
        return np.multiply(self.binary_npy, veins_of_this_body.binary_npy).sum() / self.binary_npy.sum()


class ScanLinesMicroImage(MicroImage):

    def __init__(self, path):
        self.dtype = cfg.SCANLINES_DTYPE
        super().__init__(path)
        
    def _pix_to_rc(self, pix, numCols):
        return int(pix // numCols), int(pix % numCols)

    def _process(self):
        res = [cfg.SCANLINES_CHECKBYTES] + self._make_shape_repr(self.binary_npy.shape[0], self.binary_npy.shape[1])
        curr = 0
        curr_count = 0
        first_entry = True
        for pix, val in enumerate(self.binary_npy.reshape(-1)):
            if val != curr:
                # print(f"{pix} {curr_count}")
                if (first_entry):
                    row, col = self._pix_to_rc(pix, self.binary_npy.shape[1])
                    res = res + self._make_shape_repr(row, col)
                    first_entry = False
                else:
                    res.append(pix-curr_count)
                curr = val
                curr_count = pix
            elif (not first_entry) and ((pix-curr_count) == np.iinfo(self.dtype).max):
                res.append(0)
                curr_count = pix
        # for i, j in zip(res, np.array(res, dtype=self.dtype)):
        #     print(i, j)
        return np.array(res, dtype=self.dtype)

    def _inverse_process(self, processed_img):
        check_byte, data_start_idx, num_rows, num_cols = self._ret_header(processed_img)
        if processed_img[0] != cfg.SCANLINES_CHECKBYTES:
            raise ValueError("Check bytes for scanlines inverse process are incorrect")
            return None
        start_idx_so_far, rows_so_far, cols_so_far = self._ret_shape_from_repr(processed_img[data_start_idx:])
        brush = 1
        pix_so_far = rows_so_far * self.binary_npy.shape[1] + cols_so_far
        res = np.zeros((1, num_rows * num_cols), dtype=self.dtype)
        for brush_switch in processed_img[data_start_idx + start_idx_so_far:]:
            if brush_switch == 0:
                res[0, pix_so_far : pix_so_far + np.iinfo(self.dtype).max] = brush
                pix_so_far += np.iinfo(self.dtype).max
            else:
                res[0, pix_so_far : pix_so_far + brush_switch] = brush
                pix_so_far += brush_switch
                brush = 1 - brush
        res = res.reshape(num_rows, num_cols)
        res_img = self._bin_npy_to_raw(res)
        plt.imshow(res_img, cmap='gray')
        plt.show()
        return res_img

    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.npy")
        np.save(path, self.processed)

    def print_memory(self):
        print("---RAW---")
        print(f"total size of raw data (bytes): {self.raw_size}")
        print("")

        print("---BINARY_NPY---")
        print(f"num elements : {self.binary_npy.size}")
        print(f"size of each element (bytes): {self.binary_npy.itemsize}")
        print(f"total size of binary numpy data (bytes): {self.binary_npy.nbytes}")
        print("")

        print("---PROCESSED---")
        print(f"num elements : {self.processed.size}")
        print(f"size of each element (bytes): {self.processed.itemsize}")
        print(f"total size of processed data (bytes): {self.processed.nbytes}")
        print("")


class BitMapMicroImage(MicroImage):

    def __init__(self, path):
        self.dtype = cfg.BITMAP_DTYPE
        super().__init__(path)

    def _process(self):
        bin_npy_vector = self.binary_npy.reshape(-1)
        res = [cfg.BITMAP_CHECKBYTES] + self._make_shape_repr(self.binary_npy.shape[0], self.binary_npy.shape[1])
        for i in range(0, bin_npy_vector.size, 8):
            bin_int = int("".join(map(str, bin_npy_vector[i:i+8])), 2)
            res.append(bin_int)
        return np.array(res, dtype=self.dtype)

    def _inverse_process(self, processed_img):
        check_byte, data_start_idx, num_rows, num_cols = self._ret_header(processed_img)
        if check_byte != cfg.BITMAP_CHECKBYTES:
            raise ValueError("Check bytes for bitmap inverse process are incorrect")
            return None
        bin_npy_1d = []
        for pix, val in enumerate(self.processed[data_start_idx:]):
            a = self._cvt_b10_b2(val)
            bin_npy_1d += a 
        bin_npy = np.array(bin_npy_1d, dtype="uint8").reshape(num_rows, num_cols)
        img = self._bin_npy_to_raw(bin_npy)
        plt.imshow(img, cmap='gray')
        plt.show()
        return img

    def _cvt_b10_b2(self, b10):
        if b10 == 0:
            return [0] * 8
        b2 = [int(char) for char in bin(int(b10))[2:]]
        return [0] * (8 - len(b2)) + b2
    
    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.npy")
        np.save(path, self.processed)

    def print_memory(self):
        print("---RAW---")
        print(f"total size of raw data (bytes): {self.raw_size}")
        print("")

        print("---BINARY_NPY---")
        print(f"num elements : {self.binary_npy.size}")
        print(f"size of each element (bytes): {self.binary_npy.itemsize}")
        print(f"total size of binary numpy data (bytes): {self.binary_npy.nbytes}")
        print("")

        print("---PROCESSED---")
        print(f"num elements : {self.processed.size}")
        print(f"size of each element (bytes): {self.processed.itemsize}")
        print(f"total size of processed data (bytes): {self.processed.nbytes}")
        print("")

class Base64MicroImage(MicroImage):

    def __init__(self, path):
        super().__init__(path)

    def _process(self):
        buffer = BytesIO()
        self.raw.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue())

    def _inverse_process(self, processed_img):
        img_bytes = base64.b64decode(processed_img)
        buf = BytesIO(img_bytes)
        img = Image.open(buf)
        plt.imshow(img, cmap='gray')
        plt.show()
        return img

    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.out")
        with open(path, "wb") as outfile: 
            outfile.write(self.processed)

    def print_memory(self):
        print("---RAW---")
        print(f"total size of raw data (bytes): {self.raw_size}")
        print("")

        print("---BINARY_NPY---")
        print(f"num elements : {self.binary_npy.size}")
        print(f"size of each element (bytes): {self.binary_npy.itemsize}")
        print(f"total size of binary numpy data (bytes): {self.binary_npy.nbytes}")
        print("")

        print("---PROCESSED---")
        print(f"total size of processed data (bytes): {getsizeof(self.processed)}")
        print("")

if __name__ == "__main__":
    path = os.path.join(cfg.COLLECTED_DIR, "small_sess_0.png")
    body = ScanLinesMicroImage(path)
    # body.show_binary_img()
    # body.print_memory()
    # print(body.validate_process())
    # body.save_processed_img("trial")

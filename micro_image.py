import config as cfg
import numpy as np
import os
from PIL import Image
import matplotlib.pyplot as plt


'''
Image level data and methods
'''


class MicroImage():

    def __init__(self, path):
        self.raw = self.read_img(path)
        self.processed = self._process()

    def read_img(self, path):
        return ((255-np.asarray(Image.open(path))) / 255).astype(np.uint8)

    def show_img(self):
        plt.imshow((1-self.raw)*255, cmap='gray')
        plt.show()

    def _process(self):
        raise NotImplementedError

    def print_memory(self):
        print("---RAW---")
        print(f"num elements : {self.raw.size}")
        print(f"size of each element (bytes): {self.raw.itemsize}")
        print(f"total size of raw data (bytes): {self.raw.nbytes}")

        print("---PROCESSED---")
        print(f"num elements : {self.processed.size}")
        print(f"size of each element (bytes): {self.processed.itemsize}")
        print(f"total size of processed data (bytes): {self.processed.nbytes}")


class ScanLinesMicroImage(MicroImage):

    def __init__(self, path):
        super().__init__(path)

    def _process(self):
        res = [self.raw.shape[0], self.raw.shape[1]]
        curr = 0
        curr_count = 0
        for pix in range(self.raw.size):
            row, col = self._pix_to_rc(pix, self.raw.shape[1])
            if self.raw[row, col] != curr:
                res.append(pix-curr_count)
                curr = self.raw[row, col]
                curr_count = pix
        return np.array(res, dtype="uint16")

    def _inverse_process(self):
        res = np.zeros((self.processed[0], self.processed[1]))
        brush = 0
        pix_so_far = 0
        for brush_switch in self.processed[2:]:
            s_row, s_col = self._pix_to_rc(pix_so_far, self.raw.shape[1])
            e_row, e_col = self._pix_to_rc(pix_so_far + brush_switch, self.raw.shape[1])
            # print(f"{s_row}, {s_col}, {e_row}, {e_col}")
            if s_row == e_row:
                res[s_row, s_col:e_col] = brush
            else:
                res[s_row, s_col:] = brush
                for row in range(s_row + 1, e_row):
                    res[row, :] = brush
                res[e_row, :e_col] = brush
            brush = 1 - brush
            pix_so_far += brush_switch
        plt.imshow((1-res)*255, cmap='gray')
        plt.show()
        return res

    def _pix_to_rc(self, pix, numCols):
        return int(pix // numCols), int(pix % numCols)

    def validate_process(self):
        return np.array_equal(self.raw, self._inverse_process())



class BitMapMicroImage(MicroImage):

    def __init__(self, path):
        super().__init__(path)


if __name__ == "__main__":
    path = os.path.join(cfg.COLLECTED_DIR, "raw_sess_0.png")
    body = ScanLinesMicroImage(path)
    body.show_img()
    body.print_memory()
    print(body.validate_process())

    # def _process(self):
    #     res = [self.raw.shape[0], self.raw.shape[1]]
    #     curr = 0
    #     for pix in range(self.raw.size):
    #         row, col = self._pix_to_rc(pix, self.raw.shape[1])
    #         if self.raw[row, col] != curr:
    #             res.append(row*self.raw.shape[1]+col)
    #             curr = self.raw[row, col]
    #     return np.array(res, dtype="uint64")

    # def _inverse_process(self):
    #     res = np.zeros((self.processed[0], self.processed[1]))
    #     brush = 1
    #     for start, end in zip(self.processed[2:], self.processed[3:]):
    #         s_row, s_col = self._pix_to_rc(start, self.raw.shape[1])
    #         e_row, e_col = self._pix_to_rc(end, self.raw.shape[1])
    #         # print(f"{s_row}, {s_col}, {e_row}, {e_col}")
    #         if s_row == e_row:
    #             res[s_row, s_col:e_col] = brush
    #         else:
    #             res[s_row, s_col:] = brush
    #             for row in range(s_row + 1, e_row):
    #                 res[row, :] = brush
    #             res[e_row, :e_col] = brush
    #         brush = 1 - brush
    #     plt.imshow((1-res)*255, cmap='gray')
    #     plt.show()
    #     return res
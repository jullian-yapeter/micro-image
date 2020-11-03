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
        self.raw = self.read_img(path) # 1 for subject and 0 for background
        self.processed = self._process()

    def read_img(self, path):
        im_arr = np.asarray(Image.open(path))
        # print(im_arr.nbytes)
        return ((255-im_arr) / 255).astype(np.uint8)

    def show_img(self):
        plt.imshow((1-self.raw)*255, cmap='gray')
        plt.show()

    def _process(self):
        raise NotImplementedError

    def save_processed_img(self, filename):
        path = os.path.join(cfg.PROCESSED_DIR, f"{filename}.npy")
        np.save(path, self.processed)

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
        self.dtype = "uint16"
        super().__init__(path)
        
    def _process(self):
        res = [self.raw.shape[0], self.raw.shape[1]]
        curr = 0
        curr_count = 0
        first_entry = True
        for pix in range(self.raw.size):
            row, col = self._pix_to_rc(pix, self.raw.shape[1])
            if self.raw[row, col] != curr:
                # print(f"{pix} {curr_count}")
                if (first_entry):
                    res.append(row)
                    res.append(col)
                    first_entry = False
                else:
                    if pix-curr_count > np.iinfo(self.dtype).max:
                        for i in range((pix-curr_count)//np.iinfo(self.dtype).max):
                            res.append(0)
                        res.append((pix-curr_count) % np.iinfo(self.dtype).max)
                    else:
                        res.append(pix-curr_count)
                curr = self.raw[row, col]
                curr_count = pix
        return np.array(res, dtype=self.dtype)

    def _inverse_process(self):
        res = np.zeros((self.processed[0], self.processed[1]))
        print(res.shape)
        brush = 1
        pix_so_far = self.processed[2] * self.raw.shape[1] + self.processed[3]
        for brush_switch in self.processed[4:]:
            s_row, s_col = self._pix_to_rc(pix_so_far, self.raw.shape[1])
            if brush_switch == 0:
                e_row, e_col = self._pix_to_rc(pix_so_far + np.iinfo(self.dtype).max, self.raw.shape[1])
                # print(e_row, e_col)
            else:
                e_row, e_col = self._pix_to_rc(pix_so_far + brush_switch, self.raw.shape[1])
                # print(e_row, e_col)
            # print(f"{s_row}, {s_col}, {e_row}, {e_col}")
            if s_row == e_row:
                res[s_row, s_col:e_col] = brush
            else:
                res[s_row, s_col:] = brush
                for row in range(s_row + 1, e_row):
                    res[row, :] = brush
                res[e_row, :e_col] = brush
            if brush_switch == 0:
                pix_so_far += np.iinfo(self.dtype).max
            else:
                pix_so_far += brush_switch
                brush = 1 - brush
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
    path = os.path.join(cfg.COLLECTED_DIR, "big_sess_0.png")
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
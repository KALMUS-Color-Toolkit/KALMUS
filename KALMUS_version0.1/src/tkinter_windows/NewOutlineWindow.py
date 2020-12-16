import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import matplotlib
from skimage.color import rgb2hsv, hsv2rgb
import numpy as np

font = {'family' : 'DejaVu Sans',
        'size'   : 8}

matplotlib.rc('font', **font)

class NewOutlineWindow():
    def __init__(self, barcode_1, barcode_2, figsize=(12, 5), dpi=100):
        self.barcode_1 = barcode_1
        self.barcode_2 = barcode_2
        self.plot_window = tkinter.Tk()
        self.plot_window.wm_title("Inspect Barcode")
        self.fig, self.ax = plt.subplots(2, 2, figsize=figsize, dpi=dpi,
                                         gridspec_kw={'width_ratios': [2.8, 1]}, sharex='col', sharey='col')

        try:
            self.ax[0][0].set_title("Color Type: {:s}    Frame Type: {:s}"
                                    .format(self.barcode_1.color_metric, self.barcode_1.frame_type))
            self.ax[1][0].set_title("Color Type: {:s}    Frame Type: {:s}"
                                    .format(self.barcode_2.color_metric, self.barcode_2.frame_type))
        except:
            pass
        self.ax[0][0].imshow(barcode_1.get_barcode().astype("uint8"))
        self.ax[1][0].imshow(barcode_2.get_barcode().astype("uint8"))

        normalized_barcode_1 = self.barcode_1.get_barcode().astype("float") / 255

        hsv_colors_1 = rgb2hsv(normalized_barcode_1.reshape(-1, 1, 3))
        self.hue_1 = hsv_colors_1[..., 0] * 360

        bin_step = 5
        N, bins, patches = self.ax[0][1].hist(self.hue_1[:, 0], bins=(np.arange(0, 361, bin_step)))

        self.paint_hue_hist(bin_step, patches)

        self.ax[0][1].set_xticks(np.arange(0, 361, 30))
        self.ax[0][1].set_xlabel("Color Hue (0 - 360)")
        self.ax[0][1].set_ylabel("Number of frames")

        normalized_barcode_2 = self.barcode_2.get_barcode().astype("float") / 255

        hsv_colors_2 = rgb2hsv(normalized_barcode_2.reshape(-1, 1, 3))
        self.hue_2 = hsv_colors_2[..., 0] * 360

        N, bins, patches = self.ax[1][1].hist(self.hue_2[:, 0], bins=(np.arange(0, 361, bin_step)))

        self.paint_hue_hist(bin_step, patches)

        self.ax[1][1].set_xticks(np.arange(0, 361, 30))
        self.ax[1][1].set_xlabel("Color Hue (0 - 360)")
        self.ax[1][1].set_ylabel("Number of frames")

        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)  # A tk.DrawingArea.
        self.canvas.draw()

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        self.toolbar.update()

        self.canvas.get_tk_widget().pack(side=tkinter.RIGHT)

    def paint_hue_hist(self, bin_step, patches):
        for i in range(len(patches)):
            hue = np.array([i * bin_step / 360.0, 1.0, 1.0]).astype("float64")
            hue = np.expand_dims(np.expand_dims(hue, 0), 0)
            rgb = hsv2rgb(hue).tolist()
            rgb_tuple = (rgb[0][0][0], rgb[0][0][1], rgb[0][0][2])
            patches[i].set_facecolor(rgb_tuple)
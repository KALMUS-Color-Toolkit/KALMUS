import tkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from skimage.color import rgb2hsv, hsv2rgb
import numpy as np
from src.visualization_utils import show_colors_in_cube


class PlotBarcodeWindow():
    def __init__(self, barcode, figsize=(6, 4), dpi=100):
        self.barcode = barcode
        self.plot_window = tkinter.Tk()
        self.plot_window.wm_title("Inspect Barcode")
        self.fig = plt.figure(figsize=figsize, dpi=dpi)

        plt.imshow(barcode.get_barcode().astype("uint8"))
        plt.axis("off")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_window)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_window)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.button_hist = tkinter.Button(master=self.plot_window, text="Show Color in RGB Cube",
                                          command=self.show_RGB_color_in_cube)
        self.button_hist.pack(side=tkinter.BOTTOM)
        self.button_hist = tkinter.Button(master=self.plot_window, text="Show Histogram",
                                          command=self.show_color_histogram)
        self.button_hist.pack(side=tkinter.BOTTOM)

        self.plot_window.mainloop()

    def show_RGB_color_in_cube(self):
        RGBColorCubeWindow(self.barcode)

    def show_color_histogram(self):
        ColorHistogramWindow(self.barcode)


class ColorHistogramWindow():
    def __init__(self, barcode):
        self.window = tkinter.Tk()
        self.window.wm_title("Colors in RGB cube")

        normalized_barcode = barcode.get_barcode().astype("float") / 255

        hsv_colors = rgb2hsv(normalized_barcode.reshape(-1, 1, 3))
        hue = hsv_colors[..., 0] * 360

        fig, ax = plt.subplots(figsize=(9, 5))

        bin_step = 5
        N, bins, patches = ax.hist(hue[:, 0], bins=(np.arange(0, 361, bin_step)))

        ax.set_xticks(np.arange(0, 361, 30))
        ax.set_xlabel("Color Hue (0 - 360)")
        ax.set_ylabel("Number of frames")

        for i in range(len(patches)):
            hue = np.array([i * bin_step / 360.0, 1.0, 1.0]).astype("float64")
            hue = np.expand_dims(np.expand_dims(hue, 0), 0)
            rgb = hsv2rgb(hue).tolist()
            rgb_tuple = (rgb[0][0][0], rgb[0][0][1], rgb[0][0][2])
            patches[i].set_facecolor(rgb_tuple)

        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.window.mainloop()


class RGBColorCubeWindow():
    def __init__(self, barcode):
        self.barcode = barcode
        self.window = tkinter.Tk()
        self.window.wm_title("Colors in RGB cube")

        fig, ax = show_colors_in_cube(self.barcode.colors, return_figure=True, figure_size=(6, 6), sampling=10000)
        canvas = FigureCanvasTkAgg(fig, master=self.window)  # A tk.DrawingArea.
        canvas.draw()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
        ax.mouse_init()

        toolbar = NavigationToolbar2Tk(canvas, self.window)
        toolbar.update()
        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.window.mainloop()
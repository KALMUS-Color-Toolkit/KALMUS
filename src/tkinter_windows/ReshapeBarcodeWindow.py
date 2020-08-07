import tkinter
from src.tkinter_windows.KALMUS_utils import get_comparison_result_text
import copy
import cv2
from PIL import ImageTk, Image


class ReshapeBarcodeWindow():
    def __init__(self, barcode, display_widget, display_image, compared_barcode, info_box):
        self.barcode = barcode
        self.display_widget = display_widget
        self.display_image = display_image
        self.compared_barcode = compared_barcode
        self.info_box = info_box

        self.window = tkinter.Tk()
        self.window.geometry("320x150")
        self.window.wm_title("Reshape/Resize Barcode Config")

        # Reshape/Resize option
        self.config_option = tkinter.StringVar(self.window)
        self.config_option.set("Reshape")  # initialize

        params_label = tkinter.Label(self.window, text="Config Params: ")
        params_label.grid(row=0, column=0, columnspan=1, sticky=tkinter.W)

        column_length_label = tkinter.Label(self.window, text="Frames per Column: ")
        column_length_label.grid(row=1, column=0, sticky=tkinter.W)

        self.column_length_entry = tkinter.Entry(self.window, textvariable="-1", width=5)
        self.column_length_entry.grid(row=1, column=1, padx=15)

        self.resize_x_label = tkinter.Label(self.window, text="Scale Width by (ratio): ")
        self.resize_x_label.grid(row=2, column=0, sticky=tkinter.W)

        self.resize_x_entry = tkinter.Entry(self.window, textvariable="-2", width=5, state="disabled")
        self.resize_x_entry.grid(row=2, column=1, padx=15)

        self.resize_y_label = tkinter.Label(self.window, text="Scale Height by (ratio): ")
        self.resize_y_label.grid(row=3, column=0, sticky=tkinter.W)

        self.resize_y_entry = tkinter.Entry(self.window, textvariable="-3", width=5, state="disabled")
        self.resize_y_entry.grid(row=3, column=1, padx=15)

        self.process_button = tkinter.Button(self.window, text="Process", command=self.reshape_resize_barcode)
        self.process_button.grid(row=4, column=1)

        config_label = tkinter.Label(self.window, text="Config options: ")
        config_label.grid(row=0, column=2, columnspan=1)

        radio_reshape = tkinter.Radiobutton(self.window, text="Reshape", variable=self.config_option,
                                            value="Reshape", anchor='w',
                                            command=self.reshape)
        radio_reshape.grid(row=1, column=2, sticky=tkinter.W)
        radio_reshape.select()

        radio_scaling = tkinter.Radiobutton(self.window, text="Scaling", variable=self.config_option,
                                            value="Scaling", anchor='w',
                                            command=self.scale)
        radio_scaling.grid(row=2, column=2, sticky=tkinter.W)

        radio_resize = tkinter.Radiobutton(self.window, text="Resize", variable=self.config_option,
                                           value="Resize", anchor='w',
                                           command=self.resize)
        radio_resize.grid(row=3, column=2, sticky=tkinter.W)

    def reshape(self):
        self.column_length_entry.config(state='normal')
        self.resize_x_entry.config(state='disabled')
        self.resize_y_entry.config(state='disabled')

    def scale(self):
        self.resize_x_label['text'] = "Scale Width by (ratio): "
        self.resize_y_label['text'] = "Scale Height by (ratio): "

        self.column_length_entry.config(state='disabled')
        self.resize_x_entry.config(state='normal')
        self.resize_y_entry.config(state='normal')

    def resize(self):
        self.resize_x_label['text'] = "Resize Width to (pixels): "
        self.resize_y_label['text'] = "Resize Height by (pixels): "

        self.column_length_entry.config(state='disabled')
        self.resize_x_entry.config(state='normal')
        self.resize_y_entry.config(state='normal')

    def reshape_resize_barcode(self):
        option = self.config_option.get()
        if option == "Reshape":
            frames_per_column = int(self.column_length_entry.get())
            self.barcode.reshape_barcode(frames_per_column)

            self.updated_new_barcode()
        elif option == "Resize":
            resized_barcode = cv2.resize(self.barcode.get_barcode(),
                                         dsize=(int(self.resize_x_entry.get()), int(self.resize_y_entry.get())),
                                         interpolation=cv2.INTER_NEAREST)
            self.barcode.barcode = resized_barcode
            self.updated_new_barcode()
        elif option == "Scaling":
            resized_barcode = cv2.resize(self.barcode.get_barcode(),
                                         dsize=(0, 0),
                                         fx=float(self.resize_x_entry.get()),
                                         fy=float(self.resize_y_entry.get()),
                                         interpolation=cv2.INTER_NEAREST)
            self.barcode.barcode = resized_barcode
            self.updated_new_barcode()

        self.window.destroy()

    def updated_new_barcode(self):
        self.display_image = ImageTk.PhotoImage(Image.fromarray(self.barcode.get_barcode().astype("uint8")))
        self.display_widget.configure(image=self.display_image)
        self.display_widget.image = self.display_image
        results_text = get_comparison_result_text(self.barcode, self.compared_barcode)
        self.info_box['text'] = results_text

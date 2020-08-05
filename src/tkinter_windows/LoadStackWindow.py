import tkinter
from src.tkinter_windows.KALMUS_utils import get_comparison_result_text
import copy
from PIL import ImageTk, Image


class LoadStackWindow():
    def __init__(self, barcode_stack, barcode, display_widget, display_image, compared_barcode, info_box):
        self.barcode_stack = barcode_stack
        self.barcode = barcode
        self.display_widget = display_widget
        self.display_image = display_image
        self.compared_barcode = compared_barcode
        self.info_box = info_box

        self.window = tkinter.Tk()
        self.window.geometry("320x400")
        self.window.wm_title("Barcodes on memory stack")
        self.listbox = tkinter.Listbox(self.window, selectmode=tkinter.SINGLE, width=80, height=20)
        self.listbox.grid(row=0, column=0)

        for barcode_names in self.barcode_stack.keys():
            self.listbox.insert(tkinter.END, barcode_names)
        self.button_load = tkinter.Button(master=self.window, text="Load Selected Barcode", command=self.load_stack)
        self.button_load.grid(row=1, column=0, sticky=tkinter.W)

    def load_stack(self):
        barcode_key = str(self.listbox.get(self.listbox.curselection()))
        self.barcode.__dict__ = copy.deepcopy(self.barcode_stack[barcode_key].__dict__.copy())

        self.display_image = ImageTk.PhotoImage(Image.fromarray(self.barcode.get_barcode().astype("uint8")))
        self.display_widget.configure(image=self.display_image)
        self.display_widget.image = self.display_image

        result_text = get_comparison_result_text(self.barcode, self.compared_barcode)
        self.info_box['text'] = result_text

        self.window.destroy()

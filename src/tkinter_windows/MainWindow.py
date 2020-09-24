from PIL import ImageTk, Image
import tkinter
from src.tkinter_windows.PlotBarcodeWindow import PlotBarcodeWindow
from src.tkinter_windows.GenerateBarcodeWindow import GenerateBarcodeWindow
from src.tkinter_windows.SaveBarcodeWindow import SaveBarcodeWindow
from src.tkinter_windows.LoadStackWindow import LoadStackWindow
from src.tkinter_windows.LoadJsonWindow import LoadJsonWindow
from src.tkinter_windows.KALMUS_utils import get_comparison_result_text
from src.tkinter_windows.ReshapeBarcodeWindow import ReshapeBarcodeWindow
from src.tkinter_windows.KALMUS_utils import resource_path
import copy


class MainWindow():
    def __init__(self, barcode_tmp, barcode_gn):
        self.root = tkinter.Tk()
        self.root.geometry("1050x480")

        image_path = resource_path("background_image.jpg")
        background_image = ImageTk.PhotoImage(Image.open(image_path))
        background_label = tkinter.Label(self.root, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1, bordermode="outside")

        self.barcode_gn = barcode_gn
        self.barcodes_stack = {"default": copy.deepcopy(barcode_tmp)}

        self.barcode_1 = copy.deepcopy(barcode_tmp)
        self.barcode_2 = copy.deepcopy(barcode_tmp)

        self.root.wm_title("KALMUS")

        self.root.barcode_display_1 = ImageTk.PhotoImage(Image.fromarray(self.barcode_1.get_barcode().astype("uint8")))
        self.display_1 = tkinter.Label(self.root, image=self.root.barcode_display_1)
        self.display_1.grid(row=0, column=1, pady=20, padx=10, columnspan=3, rowspan=4)

        self.root.barcode_display_2 = ImageTk.PhotoImage(Image.fromarray(self.barcode_2.get_barcode().astype("uint8")))
        self.display_2 = tkinter.Label(self.root, image=self.root.barcode_display_2)
        self.display_2.grid(row=4, column=1, pady=20, padx=10, columnspan=3, rowspan=4)

        button_load_1 = tkinter.Button(master=self.root, text="Load from JSON",
                                       command=self.load_json_barcode_1)
        button_load_1.grid(row=0, column=5)

        button_load_2 = tkinter.Button(master=self.root, text="Load from JSON",
                                       command=self.load_json_barcode_2)
        button_load_2.grid(row=4, column=5)

        button_load_stack_1 = tkinter.Button(master=self.root, text="Load from Memory",
                                             command=self.load_stack_barcode_1)
        button_load_stack_1.grid(row=1, column=5)

        button_load_stack_2 = tkinter.Button(master=self.root, text="Load from Memory",
                                             command=self.load_stack_barcode_2)
        button_load_stack_2.grid(row=5, column=5)

        button_barcode_1 = tkinter.Button(master=self.root, text="Inspect Barcode",
                                          command=self.show_barcode_1)
        button_barcode_1.grid(row=2, column=5)

        button_barcode_2 = tkinter.Button(master=self.root, text="Inspect Barcode",
                                          command=self.show_barcode_2)
        button_barcode_2.grid(row=6, column=5)

        button_reshape_barcode_1 = tkinter.Button(master=self.root, text="Reshape Barcode",
                                                  command=self.reshape_barcode_1)
        button_reshape_barcode_1.grid(row=3, column=5, pady=10)

        button_reshape_barcode_2 = tkinter.Button(master=self.root, text="Reshape Barcode",
                                                  command=self.reshape_barcode_2)
        button_reshape_barcode_2.grid(row=7, column=5)

        button_generate = tkinter.Button(master=self.root, text="Generate Barcode",
                                         command=self.generate_barcode)
        button_generate.grid(row=8, column=2)

        button_save = tkinter.Button(master=self.root, text="Save JSON file",
                                     command=self.save_barcode_on_stack)
        button_save.grid(row=8, column=3, sticky=tkinter.W)

        button_quit = tkinter.Button(master=self.root, text="Quit", command=self.quit)
        button_quit.grid(row=9, column=5)

        # Comparison Info panel

        result_text = get_comparison_result_text(self.barcode_1, self.barcode_2)

        self.info_label = tkinter.Label(self.root, text=result_text, width=35, bg='white', anchor='w')
        self.info_label.grid(row=0, column=0, rowspan=8, padx=10, pady=20, sticky=tkinter.W)

        self.root.mainloop()

    def quit(self):
        self.root.quit()  # stops mainloop
        self.root.destroy()  # this is necessary on Windows to prevent
        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def show_barcode_1(self):
        PlotBarcodeWindow(self.barcode_1)

    def show_barcode_2(self):
        PlotBarcodeWindow(self.barcode_2)

    def load_json_barcode_1(self):
        LoadJsonWindow(self.barcode_gn, self.barcode_1,
                       self.display_1, self.root.barcode_display_1, self.barcode_2, self.info_label,
                       self.barcodes_stack)

    def load_json_barcode_2(self):
        LoadJsonWindow(self.barcode_gn, self.barcode_2,
                       self.display_2, self.root.barcode_display_2, self.barcode_1, self.info_label,
                       self.barcodes_stack)

    def load_stack_barcode_1(self):
        LoadStackWindow(self.barcodes_stack, self.barcode_1, self.display_1, self.root.barcode_display_1,
                        self.barcode_2, self.info_label)

    def load_stack_barcode_2(self):
        LoadStackWindow(self.barcodes_stack, self.barcode_2, self.display_2, self.root.barcode_display_2,
                        self.barcode_1, self.info_label)

    def reshape_barcode_1(self):
        ReshapeBarcodeWindow(self.barcode_1, self.display_1, self.root.barcode_display_1,
                             self.barcode_2, self.info_label)

    def reshape_barcode_2(self):
        ReshapeBarcodeWindow(self.barcode_2, self.display_2, self.root.barcode_display_2,
                             self.barcode_1, self.info_label)

    def generate_barcode(self):
        GenerateBarcodeWindow(self.barcode_gn, self.barcodes_stack)

    def save_barcode_on_stack(self):
        SaveBarcodeWindow(self.barcodes_stack)

from src.tkinter_windows.KALMUS_utils import get_comparison_result_text
from PIL import ImageTk, Image
import tkinter.filedialog
import copy


class LoadJsonWindow():
    def __init__(self, barcode_generator, barcode, display_widget, display_image, compared_barcode, info_text,
                 barcode_stack):
        self.barcode_generator = barcode_generator
        self.barcode = barcode
        self.display_widget = display_widget
        self.display_image = display_image
        self.compared_barcode = compared_barcode
        self.info_text = info_text

        self.barcode_stack = barcode_stack

        self.window = tkinter.Tk()
        self.window.geometry("520x100")
        self.window.wm_title("Load JSON barcode")

        filename_label = tkinter.Label(self.window, text="JSON file path: ")
        filename_label.grid(row=0, column=0, sticky=tkinter.W)

        self.filename_entry = tkinter.Entry(self.window, textvariable="", width=40)
        self.filename_entry.grid(row=0, column=1, columnspan=2, sticky=tkinter.W)

        barcode_type_label = tkinter.Label(self.window, text="Specify Barcode Type: ")
        barcode_type_label.grid(row=1, column=0, sticky=tkinter.W)

        self.variable = tkinter.StringVar(self.window)
        self.variable.set("Color")

        dropdown_type = tkinter.OptionMenu(self.window, self.variable, "Color", "Brightness")
        dropdown_type.grid(row=1, column=1, sticky=tkinter.W)

        self.button_build_barcode = tkinter.Button(self.window, text="Load", command=self.build_barcode)
        self.button_build_barcode.grid(row=2, column=1, columnspan=1)

        self.button_browse_folder = tkinter.Button(self.window, text="Browse", command=self.browse_folder)
        self.button_browse_folder.grid(row=0, column=3)

    def browse_folder(self):
        filename = tkinter.filedialog.askopenfilename(initialdir="/", title="Select JSON file",
                                                      filetypes=(("json files", "*.json"), ("txt files", "*.txt"),
                                                                 ("All files", "*.*")))
        self.filename_entry.delete(0, tkinter.END)
        self.filename_entry.insert(0, filename)

    def build_barcode(self):
        filename = self.filename_entry.get()
        self.barcode_generator.generate_barcode_from_json(filename, self.variable.get())
        self.barcode.__dict__ = self.barcode_generator.get_barcode().__dict__.copy()

        self.display_image = ImageTk.PhotoImage(Image.fromarray(self.barcode.get_barcode().astype("uint8")))
        self.display_widget.configure(image=self.display_image)
        self.display_widget.image = self.display_image

        results_text = get_comparison_result_text(self.barcode, self.compared_barcode)
        self.info_text['text'] = results_text

        start_pos = filename.rfind("/") + 1
        if start_pos < 0:
            start_pos = 0
        barcode_name = filename[start_pos: filename.rfind(".json")]
        self.barcode_stack[barcode_name] = copy.deepcopy(self.barcode)

        self.window.destroy()

import tkinter


class SaveBarcodeWindow():
    def __init__(self, barcode_stack):
        self.barcode_stack = barcode_stack

        self.window = tkinter.Tk()
        self.window.geometry("320x400")
        self.window.wm_title("Barcodes on memory stack")
        self.listbox = tkinter.Listbox(self.window, selectmode=tkinter.MULTIPLE, width=80, height=20)
        self.listbox.grid(row=0, column=0)

        for barcode_names in self.barcode_stack.keys():
            self.listbox.insert(tkinter.END, barcode_names)
        self.button_load = tkinter.Button(master=self.window, text="Saved Selected Barcode into JSON", command=self.load_stack)
        self.button_load.grid(row=1, column=0, sticky=tkinter.W)

    def load_stack(self):
        selected_barcode_names = [self.listbox.get(idx) for idx in self.listbox.curselection()]
        self.button_load['text'] = 'Processing...'
        for barcode_name in selected_barcode_names:
            barcode = self.barcode_stack[barcode_name]
            barcode.save_as_json("saved_json_barcode/" + barcode_name + ".json")

        self.window.destroy()

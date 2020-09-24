from src.ColorBarcodeGenerator import BarcodeGenerator
from src.tkinter_windows.MainWindow import MainWindow
from src.tkinter_windows.KALMUS_utils import resource_path


barcode_gn = BarcodeGenerator()
json_path = resource_path("mission_impossible_Bright_Whole_frame_Color.json")
barcode_gn.generate_barcode_from_json(json_file_path=json_path,
                                     barcode_type="Color")

barcode_tmp = barcode_gn.get_barcode()

MainWindow(barcode_tmp, barcode_gn)

from KALMUS.src.ColorBarcodeGenerator import BarcodeGenerator
from KALMUS.src.tkinter_windows.MainWindow import MainWindow


barcode_gn = BarcodeGenerator()
barcode_gn.generate_barcode_from_json(json_file_path="json_barcodes/1996_03_mission_impossible.mp4_Bright_Whole_frame_Color.json",
                                     barcode_type="Color")

barcode_tmp = barcode_gn.get_barcode()

MainWindow(barcode_tmp, barcode_gn)

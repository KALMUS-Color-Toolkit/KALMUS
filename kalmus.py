""" Main function of the kalmus software """

from kalmus.BarcodeGenerator import BarcodeGenerator
from kalmus.tkinter_windows.MainWindowVersion2 import MainWindow
from kalmus.tkinter_windows.KALMUS_utils import resource_path


# Instantiate the barcode generator object
barcode_gn = BarcodeGenerator()
# Build the default barcode from the default json file
json_path = resource_path("mission_impossible_Bright_Whole_frame_Color.json")
barcode_gn.generate_barcode_from_json(json_file_path=json_path,
                                      barcode_type="Color")

# Get the default barcode
barcode_tmp = barcode_gn.get_barcode()

# Use the default barcode and the barcode generator to Instantiate the Main window of the kalmus software (GUI)
MainWindow(barcode_tmp, barcode_gn)

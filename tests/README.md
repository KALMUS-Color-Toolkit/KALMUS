[![codecov](https://codecov.io/gh/KALMUS-Color-Toolkit/KALMUS/branch/master/graph/badge.svg)](https://codecov.io/gh/KALMUS-Color-Toolkit/KALMUS)
[![codecov workflow](https://github.com/KALMUS-Color-Toolkit/KALMUS/actions/workflows/test-codecov.yml/badge.svg)](https://github.com/KALMUS-Color-Toolkit/KALMUS/actions/workflows/test-codecov.yml)

# Automated Test Suite

We provide an automated tests suite for you to validate the package's core functionality.
The modules being tested including:  
```python
from kalmus.barcodes.Barcode import *
from kalmus.barcodes.BarcodeGenerator import *
from kalmus.utils.artist import *
from kalmus.utils.measure_utils import *
from kalmus.utils.visualization_utils import *
from kalmus.tkinter_windows.gui_utils import *
from kalmus.command_line_generator import *
```

A [GitHub Action](../.github/workflows/test-codecov.yml) will run on every push or pull-request to the master branch 
and upload the coverage report on [Codecov](https://app.codecov.io/gh/KALMUS-Color-Toolkit/KALMUS).   

# Contributors

We kindly ask our contributors to include the automated tests of new functionality in this test suite. We wish 
you to make sure the existing and new tests pass locally before you open a pull-request. See our 
[pull-request template](../.github/pull_request_template.md) for more details.

To run the test suite locally:
- Clone the project to your local file system.
- Make sure you are in the top directory of the cloned project
- Make sure your python version is 3.7 or 3.8 `$ python --version`
- Make sure you have the latest version of pip `$ python -m pip install --upgrade pip`
```
    $ pip install pytest
    $ pip install pytest-cov
    $ pip install .
    $ python -m pytest tests --cov=kalmus --cov-config=.coveragerc --cov-report term-missing 
```
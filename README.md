[![Project Status](https://img.shields.io/pypi/status/kalmus.svg)](https://pypi.org/project/kalmus/)
[![Python Version](https://img.shields.io/pypi/pyversions/kalmus.svg)](https://pypi.org/project/kalmus/)
[![PyPI Version](https://img.shields.io/pypi/v/kalmus.svg)](https://pypi.org/project/kalmus/)
[![codecov](https://codecov.io/gh/KALMUS-Color-Toolkit/KALMUS/branch/master/graph/badge.svg)](https://codecov.io/gh/KALMUS-Color-Toolkit/KALMUS)
[![License](https://img.shields.io/pypi/l/kalmus.svg)](https://pypi.org/project/kalmus/)
![codecov workflow](https://github.com/KALMUS-Color-Toolkit/KALMUS/actions/workflows/test-codecov.yml/badge.svg)
![build workflow](https://github.com/KALMUS-Color-Toolkit/KALMUS/actions/workflows/python-package.yml/badge.svg)

# KALMUS

KALMUS is a Python package for the computational analysis of colors in films. 
It provides quantitative tools to study and compare the use of film color. 
This package serves two purposes: (1) various ways to measure, calculate and compare a film's colors 
and (2) various ways to visualize a film's color. We have named the software KALMUS in homage to 
Natalie Kalmus (1882 - 1965), a Technicolor Director who oversaw the color palettes of nearly 300 
Hollywood feature films.

- What is a Color Barcode: [KALMUS: tools for color analysis of films](paper/joss-paper.md)   
- How can I install the KALMUS: [KALMUS Installation Guide](https://kalmus-color-toolkit.github.io/KALMUS/install.html) 
and [KALMUS PyPI Homepage](https://pypi.org/project/kalmus/).
- How do I contribute to the KALMUS: [KALMUS Contribution Guidelines](CODE_OF_CONDUCT.md)
- How to run KALMUS's automated test suite: [Auomated Test Suite](tests/)


# API Documentation

The KALMUS API reference is now available on 
[https://kalmus-color-toolkit.github.io/KALMUS/](https://kalmus-color-toolkit.github.io/KALMUS/).

# Instruction

The kalmus package requires a python with version 3.7 or 3.8.

The package is released on PyPI ([Project Homepage](https://pypi.org/project/kalmus/)). After you install the
python==3.7, 3.8, you can install the kalmus using pip (recommended)

    $ pip install kalmus


Alternatively, you could install the kalmus locally by first cloning this GitHub repo.
Then, move to the top directory of cloned kalmus project folder and install using pip command

    $ pip install .

In both methods, the package's dependencies will be automatically installed. You can verify if the kalmus has been
installed in your environment using pip command

    $ pip show kalmus

Once the package is installed. The functionalities of the KALMUS are accessible through the Graphic user interface (GUI) and imported kalmus module.

- To start the KALMUS in GUI, use the command `$ kalmus-gui`. The initiation process may take up a minute.
- To import the kalmus module in the python script, use `import kalmus`.

```jupyter
>>> import kalmus
>>> print(kalmus.__version__) # Warning: The __version__ attribute is not available in the kalmus v.1.3.6 and backward
>>> 1.3.7 
```

# Contribution

We encourage contributions, including bug fixes and new features, from our community users. When contributing to the 
kalmus package, please first contact the project maintainers by [email](yc015@bucknell.edu) or opening an issue. If 
your bug fixex or new features changing the current behavior of package, please specify the changed behaviors and 
reasons for changing in the discussion with project maintainers. 

We encourage inclusive and friendly discussion. Please follow our [code of conduct](CODE_OF_CONDUCT.md) when 
communicating. 

# Precomputed Barcodes

Precomputed barcodes are accessible upon requests. Please email the Project maintainer Yida Chen <yc015@bucknell.edu> 
about your needs. 

# Acknowledgment

The authors wish to thank the Mellon Foundation, the Dalal Family Foundation, and the Bucknell University Humanities 
Center for their support on this project.
The project is released under the open-source MIT License.

# Update Log

The full update log (from [v1.3.0](https://pypi.org/project/kalmus/1.3.0/) to [v1.3.7](https://pypi.org/project/kalmus/)) 
is now available on [https://kalmus-color-toolkit.github.io/KALMUS/update_log.html](https://kalmus-color-toolkit.github.io/KALMUS/update_log.html)

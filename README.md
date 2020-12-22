# KALMUS

KALMUS is a Python package for the computational analysis of colors in films. It addresses how to best describe a film's color.  This package is optimized for two purposes:  (1) various ways to measure, calculate and compare a film's color and (2) various ways to visualize a film's color.

# Summary

Filmmakers, cinematographers, production designers, and then colorists (the person who fine tunes or grades the color in post production) spend enormous sums and labor deciding a film’s color palette. Why? Because color has an almost subliminal impact on how we perceive a film. Interpreting a film’s use of color, however, remains an elusive and understudied area. Despite how color shades a film’s meaning, the way audiences read color remains highly subjective.  Moreover, as a time-based medium, understanding the patterning of color over the length of an entire film proves difficult for the typical viewer to see. KALMUS allows researchers to look at general patterns and trends in the use of color.  It is useful to sometimes be able to process a large number of films, to quickly visualize their color palette and to compare the use of color in two films.

KALMUS addresses these needs by (1) providing an interface that takes in either a video file (list formats here) or as a processed JSON file (files available for download), (2) allowing for the computation of a frame's "average" color in a number of ways, (3) allowing for the computation of a film's "average" color in a number of ways, (4) allowing for the segmentation of a frame in a number of ways and the subsequent computation of the color of various parts of the image, (5) providing an implementation of various ways to compare colors of two films, and (6) providing implementations of a few ways to visualize the color of a film, in particular, as color bar codes, as the 3D-plots in RBG-space and as histograms.

# Instruction
Once the package is installed. The functionalities of the KALMUS are accessible through the Graphic user interface (GUI) and imported kalmus module.

- To start the KALMUS in GUI, use the command `kalmus-gui`. The initiation process may take minutes to be finished.
- To import the kalmus module in the python script, use `import kalmus`.

# Precomputed Barcodes

Precomputed barcodes are accessible upon requests. Please email the Project maintainer Yida Chen, <yc015@bucknell.edu>, about your needs. 

# Acknowledgment

The KALMUS project is supported through the Mellon Academic Year Research Fellowships from Bucknell University. It is released under open-source MIT License.

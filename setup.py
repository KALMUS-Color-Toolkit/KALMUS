import os
from setuptools import setup, find_packages

dir_path = os.path.abspath(os.path.dirname(__file__))
path_to_md = os.path.join(dir_path, "PyPI_README.md")

with open(path_to_md, encoding='utf-8') as f:
    readme = f.read()
f.close()

setup(name='kalmus',
      version='1.3.15a',
      description='kalmus film color analysis tool',
      keywords='film, color analysis, data visualization',
      long_description=readme,
      long_description_content_type="text/markdown",
      url='https://github.com/KALMUS-Color-Toolkit/KALMUS',
      author='Yida Chen, Eric Faden, Nathan Ryan',
      author_email='yc015@bucknell.edu',
      license='MIT',
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          "Programming Language :: Python :: 3.13",
          "Programming Language :: Python :: 3.14",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Education",
          "Intended Audience :: Science/Research",
          "Operating System :: OS Independent",
          "Topic :: Multimedia :: Video",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces"
      ],
      packages=find_packages(),
      python_requires='>=3.10',
      install_requires=[
          'numpy>=1.23',
          # headless variant: same cv2 API, no X/GL system libs required.
          # kalmus uses cv2 only for image-processing (VideoCapture, cvtColor,
          # kmeans, grabCut, ...); the GUI is tkinter, never cv2.imshow.
          'opencv-python-headless>=4.6',
          'scikit-image>=0.21',  # channel_axis kwarg replaces multichannel
          'matplotlib>=3.5',
          'scikit-learn>=1.1',
          'biopython>=1.80',     # PairwiseAligner is the supported aligner
          'scipy>=1.11',         # stats.mode keepdims default change handled
          'kiwisolver>=1.4',
          'pandas>=1.5',
      ],
      entry_points={
          'console_scripts': ['kalmus-gui=kalmus.command_line_gui:main',
                              'kalmus-generator=kalmus.command_line_generator:main'],
      },
      include_package_data=True,
      zip_safe=False)

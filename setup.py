import os
from setuptools import setup, find_packages

dir_path = os.path.abspath(os.path.dirname(__file__))
path_to_md = os.path.join(dir_path, "PyPI_README.md")

with open(path_to_md, encoding='utf-8') as f:
    readme = f.read()
f.close()

setup(name='kalmus',
      version='1.3.10',
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
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Education",
          "Intended Audience :: Science/Research",
          "Operating System :: OS Independent",
          "Topic :: Multimedia :: Video",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Software Development :: User Interfaces"
      ],
      packages=find_packages(),
      python_requires='>=3.7',
      install_requires=['numpy', 'opencv-python', 'scikit-image>=0.16.2', 'matplotlib>=3.2.2',
                        'scikit-learn', 'biopython', 'scipy', 'kiwisolver>=1.3.1', 'pandas'],
      entry_points={
          'console_scripts': ['kalmus-gui=kalmus.command_line_gui:main',
                              'kalmus-generator=kalmus.command_line_generator:main'],
      },
      include_package_data=True,
      zip_safe=False)

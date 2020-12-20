from setuptools import setup, find_packages


setup(name='kalmus',
      version='1.2.0',
      description='kalmus film color analysis tool',
      keywords='film, color analysis, data visualization',
      url='https://github.com/yc015/KALMUS',
      author='Yida Chen',
      author_email='yc015@bucknell.edu',
      license='MIT',
      packages=find_packages(),
      python_requires='>=3.7',
      install_requires=['numpy','opencv-python', 'scikit-image==0.16.2', 'matplotlib==3.2.2',
                        'scikit-learn', 'biopython', 'scipy'],
      entry_points={
            'console_scripts': ['kalmus-gui=src.command_line_gui:main'],
      },
      include_package_data=True,
      zip_safe=False)
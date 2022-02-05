from setuptools import setup, Extension
import numpy as np

ext = Extension('_module2', ['_module2.c'],
                extra_compile_args=['-std=c99'],
                include_dirs=[np.get_include()])
setup(name='example', py_modules=['module1', 'module2'], ext_modules=[ext])

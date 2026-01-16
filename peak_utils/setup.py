from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

extensions = [
    Extension(
        "peak_utils.matrix",
        ["src/peak_utils/matrix.pyx"],
    ),
]

setup(
    name="peak_utils",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    ext_modules=cythonize(extensions)
)

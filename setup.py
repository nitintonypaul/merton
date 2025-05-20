from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        "mcs_simulator",
        ["cpp/sim.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++"
    ),
]

setup(
    name="mcs_simulator",
    version="0.0.1",
    ext_modules=ext_modules,
)

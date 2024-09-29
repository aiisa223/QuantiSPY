from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys
import os
import subprocess
import pybind11


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        cmake_args = ['-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=' + extdir,
                      '-DPYTHON_EXECUTABLE=' + sys.executable,
                      '-DPYBIND11_CMAKE_DIR=' + pybind11.get_cmake_dir(),
                      '-DCMAKE_PREFIX_PATH=' + pybind11.get_cmake_dir()]

        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]

        cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]

        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # Change the working directory to the project root
        project_root = os.path.abspath(os.path.dirname(__file__))

        subprocess.check_call(['cmake', project_root] + cmake_args, cwd=self.build_temp)
        subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)

        print("pybind11 path:", pybind11.get_cmake_dir())  # Debug print


setup(
    name='QuantiSPY',
    version='0.1',
    author='Ali Imran',
    author_email='0.0aliimran0.01#gmail.com',
    description='A stock analysis tool with HMM',
    long_description='',
    ext_modules=[CMakeExtension('cpp_hmm')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    packages=['python'],
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
        'alpha_vantage',
        'yfinance',
        'pybind11>=2.6.0',
    ],
    setup_requires=['pybind11>=2.6.0'],
)

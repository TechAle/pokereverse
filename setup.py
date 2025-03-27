from setuptools import setup, Extension

module = Extension(
    'mach',
    sources=['mach.c'],
    # Remove this line: libraries=['mach'],
)

setup(
    name='MachModule',
    version='1.0',
    description='Python interface to Mach APIs',
    ext_modules=[module],
)
"""Galileo SSI setup."""

from setuptools import setup


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

with open('README.rst', 'r') as f:
    long_description = f.read()


setup(
    name='galileo-ssi',
    version='1.6.1',
    description='Python parser for Galileo SSI instrument',
    author='Benoit Seignovert',
    author_email='benoit.a.seignovert@jpl.nasa.gov',
    url='https://github.com/seignovert/galileo-ssi',
    install_requires=requirements,
    python_requires='>=3.6',
    license='MIT',
    packages=['ssi', 'ssi.isis', 'ssi.geol'],
    long_description=long_description,
    include_package_data=True,
)

"""Galileo SSI setup."""

from setuptools import setup


with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='ssi',
    version='0.1',
    description='Python parser for Galileo SSI instrument',
    author='Benoit Seignovert',
    author_email='benoit.a.seignovert@jpl.nasa.gov',
    install_requires=requirements,
)

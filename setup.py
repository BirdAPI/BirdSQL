import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "birdsql",
    version = "0.6.0",
    author = "Anthony Casagrande",
    author_email = "birdapi@gmail.com",
    description = ("Very simple and basic MySQL speaking objects for python"),
    license = "MIT",
    keywords = "mysql birdapi sql orm",
    url = "https://pypi.python.org/pypi/birdsql",
    packages=['birdsql'],
    long_description=read('README.md'),
    install_requires=[
        "MySQL-python"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Database",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
)
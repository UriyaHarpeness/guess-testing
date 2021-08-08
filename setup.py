import os
import pathlib
from pathlib import Path
from typing import Union

from setuptools import find_packages, setup

import versioneer

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


def read(file_path: Union[str, pathlib.Path]) -> str:
    return open(ROOT_DIR / file_path).read()


setup(
    name='guess_testing',
    author='Uriya Harpeness',
    author_email='uriya1998@gmail.com',
    description='A tool for making coverage and edge cases seeking easier.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url="https://github.com/UriyaHarpeness/guess-testing",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(exclude=('examples',)),
    install_requires=[],
    python_requires='>=3.6'
)

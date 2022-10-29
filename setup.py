#!/usr/bin/env python3
# Copyright 2022 Jason C. Nucciarone
# See LICENSE file for licensing details.

from setuptools import setup, find_packages


setup(
    name="hpc-workshop",
    version="0.1.0",
    description="A helper program for the HPC workshop at the 2022 Ubuntu Summit - Prague",
    author="Jason C. Nucciarone",
    author_email="nucci.programming@gmail.com",
    license="Apache-2.0",
    python_requires=">=3.8",
    packages=find_packages(
        where="src",
        include=["hpcworkshop*"],
    ),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": ["hpc-workshop=hpcworkshop.main:main"]
    },
    install_requires=[
        "pylxd",
    ],
    keywords=[
        "tutorial",
        "learning",
        "hpc",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

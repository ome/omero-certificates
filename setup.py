#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OMERO server certificate management plugin
"""

import setuptools


setuptools.setup(
    name="omero-certificates",
    author="The Open Microscopy Team",
    author_email="ome-devel@lists.openmicroscopy.org.uk",
    description="OMERO server certificate management plugin",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="GPLv2",
    url="https://github.com/ome/omero-certificates",
    packages=["omero_certificates", "omero.plugins"],
    setup_requires=["setuptools_scm"],
    install_requires=["omero-py>=5.6.0", "distro==1.8.0"],
    use_scm_version={"write_to": "omero_certificates/_version.py"},
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2" " (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Software Distribution",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    tests_require=["pytest"],
)

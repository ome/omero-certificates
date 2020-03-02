#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OMERO setup and database management plugin
"""

import sys
from omero.cli import CLI
from omero_certificates.cli import CertificatesControl

HELP = "OMERO server certificate management"
try:
    register("certificates", CertificatesControl, HELP)  # noqa
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("certificate", CertificatesControl, HELP)
        cli.invoke(sys.argv[1:])

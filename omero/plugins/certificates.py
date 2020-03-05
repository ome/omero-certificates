#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OMERO setup and database management plugin
"""

import sys
from omero.cli import CLI
from omero_certificates.cli import CertificatesControl

HELP = """OMERO server certificate management

Creates self-signed certificates and adds IceSSL configuration properties to
the OMERO.server configuration to enable use of the certificates. The OMERODIR
environment variables must be set to the location of OMERO.server.
"""

try:
    register("certificates", CertificatesControl, HELP)  # noqa
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("certificate", CertificatesControl, HELP)
        cli.invoke(sys.argv[1:])

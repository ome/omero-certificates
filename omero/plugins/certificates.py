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
the OMERO.server configuration to enable use of the certificates.

The OMERODIR environment variable must be set to the location of OMERO.server.

OMERO configuration properties
------------------------------

  omero.glacier2.IceSSL.DefaultDir: The directory for storing certificates,
    defaults to {omero.data.dir}/certs

The remaining properties should only be modified by advanced users. If you do
not know what these are leave them unchanged.

  omero.certificates.commonname: The certificate subject CommonName
  omero.certificates.owner: The certificate subject excluding CommonName
  omero.certificates.key: Name of the key file
  omero.glacier2.IceSSL.CertFile: PKCS12 file name
  omero.glacier2.IceSSL.CAs: Certificate file name
  omero.glacier2.IceSSL.Password: PKCS12 password
  omero.glacier2.IceSSL.Ciphers: IceSSL ciphers
  omero.glacier2.IceSSL.ProtocolVersionMax: Maximum SSL/TLS protocol
  omero.glacier2.IceSSL.Protocols: SSL/TLS protocols
"""

try:
    register("certificates", CertificatesControl, HELP)  # noqa
except NameError:
    if __name__ == "__main__":
        cli = CLI()
        cli.register("certificate", CertificatesControl, HELP)
        cli.invoke(sys.argv[1:])

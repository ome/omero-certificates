# OMERO server certificate management plugin
[![Build Status](https://travis-ci.com/manics/omero-cli-certificates.svg?branch=master)](https://travis-ci.com/manics/omero-cli-certificates)

Generate self-signed certificates and configure OMERO.server.


## Installation

Install `openssl` if it's not already on your system.
Then activate your OMERO.server virtualenv and run:
```
pip install -U git+https://github.com/manics/omero-cli-certificates.git
```


## Usage

Set the `OMERODIR` environment variable to the location of OMERO.server.

Run:
```
omero certificates
```
to update your OMERO.server configuration and to generate or update your self-signed certificates.
If you already have the necessary configuration settings this plugin will not modify them, so it is safe to always run `omero certificates` every time you start OMERO.server.
You can now start your omero server as normal.

This plugin automatically overrides the defaults for the following properties if they're not explcitly set:
- `omero.glacier2.IceSSL.Ciphers=HIGH`: the default weaker ciphers may not be supported on some systems
- `omero.glacier2.IceSSL.ProtocolVersionMax=TLS1_2`: Support TLS 1.1 and 1.2, not just 1.0
- `omero.glacier2.IceSSL.Protocols=TLS1_0,TLS1_1,TLS1_2`: Support TLS 1.1 and 1.2, not just 1.0

The original values can be found on https://docs.openmicroscopy.org/omero/5.6.0/sysadmins/config.html#glacier2

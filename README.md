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

This plugin automatically sets `omero.glacier2.IceSSL.Ciphers` to `HIGH` since the default weaker ciphers may not be supported on some systems.
To revert to the default behaviour set it to `ADH:HIGH`.

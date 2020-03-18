# OMERO server certificate management plugin
[![Build Status](https://travis-ci.org/ome/omero-certificates.svg?branch=master)](https://travis-ci.org/ome/omero-certificates)

Generate self-signed certificates and configure OMERO.server.

If you prefer to configure OMERO manually see the examples in these documents:
- https://github.com/ome/docker-example-omero-websockets
- https://docs.openmicroscopy.org/omero/5.6.0/sysadmins/client-server-ssl.html


## Installation

Install `openssl` if it's not already on your system.
Then activate your OMERO.server virtualenv and run:
```
pip install omero-certificates
```


## Usage

Set the `OMERODIR` environment variable to the location of OMERO.server.

Run:
```
omero certificates
```
```
OpenSSL 1.1.1d  10 Sep 2019
Generating RSA private key, 2048 bit long modulus (2 primes)
.+++++
.............................+++++
e is 65537 (0x010001)
certificates created: /OMERO/certs/server.key /OMERO/certs/server.pem /OMERO/certs/server.p12
```
to update your OMERO.server configuration and to generate or update your self-signed certificates.
If you already have the necessary configuration settings this plugin will not modify them, so it is safe to always run `omero certificates` every time you start OMERO.server.
You can now start your omero server as normal.

This plugin automatically overrides the defaults for the following properties if they're not explicitly set:
- `omero.glacier2.IceSSL.Ciphers=HIGH`: the default weaker ciphers may not be supported on some systems
- `omero.glacier2.IceSSL.ProtocolVersionMax=TLS1_2`: Support TLS 1.1 and 1.2, not just 1.0
- `omero.glacier2.IceSSL.Protocols=TLS1_0,TLS1_1,TLS1_2`: Support TLS 1.1 and 1.2, not just 1.0

The original values can be found on https://docs.openmicroscopy.org/omero/5.6.0/sysadmins/config.html#glacier2

Certificates will be stored under `{omero.data.dir}/certs` by default.
Set `omero.glacier2.IceSSL.DefaultDir` to change this.

If you see a warning message such as
```
Can't load ./.rnd into RNG
```
it should be safe to ignore.

For full information see the output of:
```
omero certificates --help
```

## Developer notes

This project uses [setuptools-scm](https://pypi.org/project/setuptools-scm/).
To release a new version just create a tag.

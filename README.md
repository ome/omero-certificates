# OMERO server certificate management plugin
[![Actions Status](https://github.com/ome/omero-certificates/workflows/Tox/badge.svg)](https://github.com/ome/omero-certificates/actions)

Generate self-signed certificates and configure OMERO.server.

If you prefer to configure OMERO manually see the examples in these documents:
- https://github.com/ome/docker-example-omero-websockets
- https://docs.openmicroscopy.org/omero/latest/sysadmins/client-server-ssl.html


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
- `omero.glacier2.IceSSL.ProtocolVersionMax=TLS1_3`: Support TLS 1.2 and 1.3
- `omero.glacier2.IceSSL.Protocols=TLS1_2,TLS1_3`: Support TLS 1.2 and 1.3
- `omero.glacier2.IceSSL.DH.2048=ffdhe2048.pem`: use a pre-defined 2048-bit Diffie-Hellman group

The pre-defined Diffie-Hellman group is from [RFC 7919](https://www.rfc-editor.org/rfc/rfc7919.txt).  Newer versions of OpenSSL will prefer ECDHE and have their own 2048-bit or greater primes but it's safe to use this one.
When RHEL 7 (OpenSSL 1.0.2) support is dropped this will be removed.

__NOTE:__ If RHEL 7 is detected, only TLS 1.2 support will be enabled.

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

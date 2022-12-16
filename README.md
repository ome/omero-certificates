# OMERO server certificate management plugin
[![Actions Status](https://github.com/ome/omero-certificates/workflows/Tox/badge.svg)](https://github.com/ome/omero-certificates/actions)

Generate self-signed certificates and configure OMERO.server.

If you prefer to configure OMERO manually see the examples in these documents:
- https://github.com/ome/docker-example-omero-websockets
- https://docs.openmicroscopy.org/omero/latest/sysadmins/client-server-ssl.html


## Installation

Activate your OMERO.server virtualenv and run:
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

For full information see the output of:
```
omero certificates --help
```

## Upgrading

Since version 0.3.0 this plugin uses portable RFC 4514 (supercedes RFC 2253)
formatted strings for the `omero.certificates.owner` configuration option.  If
you have ran `omero certificates` before you may have OpenSSL command line
formatted strings in your configuration that should be updated before you can
run `omero certificates` again.  In most cases this means taking a string such
as `/L=OMERO/O=OMERO.server` and reformatting it to
`L=OMERO,O=OMERO.server`; remove the leading `/` and replace separator `/`'s
with `,`'s.

You can see the RFC 4514 compatible string for the `Issuer` and `Subject`
of your existing certificate by running:
```
openssl x509 -in /path/to/cert.pem -text -nameopt rfc2253
```

You can review the RFC in full for more specific details:
- https://tools.ietf.org/html/rfc4514.html

## Developer notes

This project uses [setuptools-scm](https://pypi.org/project/setuptools-scm/).
To release a new version just create a tag.

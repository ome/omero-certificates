#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrap openssl to manage self-signed certificates
"""

import logging
import os
import subprocess
import sys
from distro import distro
from omero.config import ConfigXml

log = logging.getLogger(__name__)


# ffdhe2048 group from RFC 7919 in PEM format
# SHA256(ffdhe2048.txt)=
#   2ef7758563185ad0dc1dbc38ab3a91647701e3ebee344fcf86b52e643bacb721
#
# The prime can be validated with OpenSSL:
#   openssl dhparam -in ffdhe2048.txt -check -text
#
# On newer versions of OpenSSL, this will print out that the group has
# been detected as "ffdhe2048":
#
# ...
#    DH Parameters: (2048 bit)
#    GROUP: ffdhe2048
# DH parameters appear to be ok.
# ...
#
# See:
#  * https://datatracker.ietf.org/doc/html/rfc7919#autoid-31
FFDHE2048_PEM = """-----BEGIN DH PARAMETERS-----
MIIBCAKCAQEA//////////+t+FRYortKmq/cViAnPTzx2LnFg84tNpWp4TZBFGQz
+8yTnc4kmz75fS/jY2MMddj2gbICrsRhetPfHtXV/WVhJDP1H18GbtCFY2VVPe0a
87VXE15/V8k1mE8McODmi3fipona8+/och3xWKE2rec1MKzKT0g6eXq8CrGCsyT7
YdEIqUuyyOP7uWrat2DX9GgdT0Kj3jlN9K5W7edjcrsZCwenyO4KbXCeAvzhzffi
7MA0BM0oNC9hkXL+nOmFg/+OTxIy7vKBg8P+OxtMb61zO7X8vC7CIAXFjvGDfRaD
ssbzSibBsu/6iGtCOGEoXJf//////////wIBAg==
-----END DH PARAMETERS-----"""


def is_rhel_7():
    major_version = distro.major_version(best=True)
    if distro.id() in ("rhel", "centos") and major_version == "7":
        return True
    return False


def update_config(omerodir):
    """
    Updates OMERO config with certificate properties if necessary
    """

    cfg = ConfigXml(os.path.join(omerodir, "etc", "grid", "config.xml"))
    cfgdict = cfg.as_map()

    def set_if_empty(cfgkey, default):
        if not cfgdict.get(cfgkey):
            cfg[cfgkey] = default
            log.info("Setting %s=%s", cfgkey, default)

    set_if_empty(
        "omero.glacier2.IceSSL.DefaultDir",
        os.path.join(cfgdict.get("omero.data.dir", "/OMERO"), "certs"),
    )
    set_if_empty("omero.certificates.commonname", "localhost")
    set_if_empty("omero.certificates.owner", "/L=OMERO/O=OMERO.server")
    set_if_empty("omero.certificates.key", "server.key")
    set_if_empty("omero.glacier2.IceSSL.CertFile", "server.p12")
    set_if_empty("omero.glacier2.IceSSL.CAs", "server.pem")
    set_if_empty("omero.glacier2.IceSSL.Password", "secret")

    if sys.platform != "darwin":
        set_if_empty("omero.glacier2.IceSSL.Ciphers", "HIGH")
    version_max = "TLS1_3"
    protocols = "TLS1_2,TLS1_3"
    if is_rhel_7():
        # RHEL 7 shipped OpenSSL, version 1.0.2, only supports up to TLS 1.2
        log.warn(
            "Your Linux distribution has been detected as RHEL 7 which will "
            "reach end of life in June 2024.  TLS 1.3 cannot be enabled and "
            "upgrading is recommended.\nSee https://www.openmicroscopy.org/"
            "2023/07/24/linux-distributions.html for more information."
        )
        version_max = "TLS1_2"
        protocols = "TLS1_2"
    set_if_empty("omero.glacier2.IceSSL.DH.2048", "ffdhe2048.pem")
    set_if_empty("omero.glacier2.IceSSL.ProtocolVersionMax", version_max)
    set_if_empty("omero.glacier2.IceSSL.Protocols", protocols)

    cfgdict = cfg.as_map()
    cfg.close()
    return cfgdict


def run_openssl(args):
    command = ["openssl"] + args
    log.info("Executing: %s", " ".join(command))
    subprocess.run(command)


def create_certificates(omerodir):
    cfgmap = update_config(omerodir)
    certdir = cfgmap["omero.glacier2.IceSSL.DefaultDir"]

    cn = cfgmap["omero.certificates.commonname"]
    owner = cfgmap["omero.certificates.owner"]
    days = "365"
    pkcs12path = os.path.join(certdir, cfgmap["omero.glacier2.IceSSL.CertFile"])
    keypath = os.path.join(certdir, cfgmap["omero.certificates.key"])
    certpath = os.path.join(certdir, cfgmap["omero.glacier2.IceSSL.CAs"])
    grouppath = os.path.join(certdir, "ffdhe2048.pem")
    password = cfgmap["omero.glacier2.IceSSL.Password"]

    try:
        run_openssl(["version"])
    except subprocess.CalledProcessError as e:
        msg = "openssl version failed, is it installed?"
        log.fatal("%s: %s", msg, e)
        raise

    os.makedirs(certdir, exist_ok=True)
    created_files = []

    # Use pre-defined Diffie-Hellman group from RFC 7919.  Newer versions
    # of OpenSSL will prefer ECDHE and have their own 2048-bit or greater
    # primes but it's safe to use this one.  When RHEL 7 (OpenSSL 1.0.2)
    # support is dropped this can be removed.
    #
    # See:
    #   * https://www.rfc-editor.org/rfc/rfc7919.txt
    with open(grouppath, "w") as pem:
        pem.write(FFDHE2048_PEM)

    # Private key
    if os.path.exists(keypath):
        log.info("Using existing key: %s", keypath)
    else:
        log.info("Creating self-signed CA key: %s", keypath)
        run_openssl(["genrsa", "-out", keypath, "2048"])
        created_files.append(keypath)

    # Self-signed certificate
    log.info("Creating self-signed certificate: %s", certpath)
    run_openssl(
        [
            "req",
            "-new",
            "-x509",
            "-subj",
            "{}/CN={}".format(owner, cn),
            "-days",
            days,
            "-key",
            keypath,
            "-out",
            certpath,
            "-extensions",
            "v3_ca",
        ]
    )
    created_files.append(certpath)

    # PKCS12 format
    log.info("Creating PKCS12 bundle: %s", pkcs12path)
    run_openssl(
        [
            "pkcs12",
            "-export",
            "-out",
            pkcs12path,
            "-inkey",
            keypath,
            "-in",
            certpath,
            "-name",
            "server",
            "-password",
            "pass:{}".format(password),
        ]
    )
    created_files.append(pkcs12path)

    return "certificates created: " + " ".join(created_files)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrap cryptography to manage self-signed certificates
"""

import logging
import os
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.hashes import SHA256, SHA1
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    pkcs12,
)
from omero.config import ConfigXml

log = logging.getLogger(__name__)


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
    set_if_empty("omero.certificates.owner", "L=OMERO,O=OMERO.server")
    set_if_empty("omero.certificates.key", "server.key")
    set_if_empty("omero.glacier2.IceSSL.CertFile", "server.p12")
    set_if_empty("omero.glacier2.IceSSL.CAs", "server.pem")
    set_if_empty("omero.glacier2.IceSSL.Password", "secret")

    set_if_empty("omero.glacier2.IceSSL.Ciphers", "HIGH")
    set_if_empty("omero.glacier2.IceSSL.ProtocolVersionMax", "TLS1_2")
    set_if_empty("omero.glacier2.IceSSL.Protocols", "TLS1_0,TLS1_1,TLS1_2")

    cfgdict = cfg.as_map()
    cfg.close()
    return cfgdict


def create_certificates(omerodir):
    cfgmap = update_config(omerodir)
    certdir = cfgmap["omero.glacier2.IceSSL.DefaultDir"]

    cn = cfgmap["omero.certificates.commonname"]
    owner = cfgmap["omero.certificates.owner"]
    days = 365
    pkcs12path = os.path.join(certdir, cfgmap["omero.glacier2.IceSSL.CertFile"])
    keypath = os.path.join(certdir, cfgmap["omero.certificates.key"])
    certpath = os.path.join(certdir, cfgmap["omero.glacier2.IceSSL.CAs"])
    password = cfgmap["omero.glacier2.IceSSL.Password"]

    os.makedirs(certdir, exist_ok=True)
    created_files = []

    # Private key
    if os.path.exists(keypath):
        log.info("Using existing key: %s", keypath)
        with open(keypath, "rb") as pem_openssl_key:
            rsa_private_key = serialization.load_pem_private_key(
                pem_openssl_key.read(),
                password=None,
            )
    else:
        log.info("Creating self-signed CA key: %s", keypath)
        # Do what `openssl genrsa -out <keypath> <numbits>` would do
        rsa_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with open(keypath, "wb") as pem_openssl_key:
            pem_openssl_key.write(
                rsa_private_key.private_bytes(
                    Encoding.PEM,
                    PrivateFormat.TraditionalOpenSSL,  # Essentially PKCS#1
                    NoEncryption(),
                )
            )
        created_files.append(keypath)

    # Self-signed certificate
    log.info("Creating self-signed certificate: %s", certpath)
    # Do what `openssl req -x509 ...` would do
    utcnow = datetime.utcnow()
    try:
        subject = issuer = x509.Name.from_rfc4514_string("{},CN={}".format(owner, cn))
    except ValueError:
        return (
            f"'omero.certificates.owner' configuration setting '{owner}' not a "
            "valid RFC 4514 string!  Are you upgrading?  See "
            "https://pypi.org/project/omero-certificates/ for help."
        )
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .not_valid_before(utcnow)
        .not_valid_after(utcnow + timedelta(days=days))
        .public_key(rsa_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .sign(rsa_private_key, SHA256())
    )
    with open(certpath, "wb") as pem_cert:
        pem_cert.write(cert.public_bytes(Encoding.PEM))
    created_files.append(certpath)

    # PKCS12 format
    log.info("Creating PKCS12 bundle: %s", pkcs12path)
    # Do what `openssl pkcs12 ...` would do
    with open(pkcs12path, "wb") as p12:
        # Maintain compatibility with OpenSSL < 3.0.0, the macOS security
        # framework and Windows.
        encryption = (
            PrivateFormat.PKCS12.encryption_builder()
            .kdf_rounds(50000)
            .key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC)
            .hmac_hash(SHA1())
            .build(password.encode("utf-8"))
        )
        p12.write(
            pkcs12.serialize_key_and_certificates(
                b"server",
                rsa_private_key,
                cert,
                None,
                encryption,
            )
        )
    created_files.append(pkcs12path)

    return "certificates created: " + " ".join(created_files)

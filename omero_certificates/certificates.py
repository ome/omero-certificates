#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Wrap openssl to manage self-signed certificates
"""

import logging
import os
import subprocess
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
    set_if_empty("omero.certificates.owner", "/L=OMERO/O=OMERO.server")
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
    password = cfgmap["omero.glacier2.IceSSL.Password"]

    try:
        run_openssl(["version"])
    except subprocess.CalledProcessError as e:
        msg = "openssl version failed, is it installed?"
        log.fatal("%s: %s", msg, e)
        raise

    os.makedirs(certdir, exist_ok=True)
    created_files = []

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

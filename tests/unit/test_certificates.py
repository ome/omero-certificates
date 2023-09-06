import os
import subprocess

from hashlib import sha256

from omero.config import ConfigXml
from omero_certificates.certificates import create_certificates, update_config


def get_config(omerodir):
    configxml = ConfigXml(os.path.join(omerodir, "etc", "grid", "config.xml"))
    try:
        return configxml.as_map()
    finally:
        configxml.close()


class TestCertificates(object):
    def test_config_from_empty(self, tmpdir):
        (tmpdir / "etc" / "grid").ensure(dir=True)
        omerodir = str(tmpdir)

        update_config(omerodir)
        cfg = get_config(omerodir)
        cfg.pop("omero.config.version")
        assert cfg == {
            "omero.glacier2.IceSSL.CAs": "server.pem",
            "omero.glacier2.IceSSL.CertFile": "server.p12",
            "omero.glacier2.IceSSL.Ciphers": "HIGH",
            "omero.glacier2.IceSSL.DH.2048": "ffdhe2048.pem",
            "omero.glacier2.IceSSL.DefaultDir": "/OMERO/certs",
            "omero.glacier2.IceSSL.Password": "secret",
            "omero.glacier2.IceSSL.ProtocolVersionMax": "TLS1_3",
            "omero.glacier2.IceSSL.Protocols": "TLS1_2,TLS1_3",
            "omero.certificates.commonname": "localhost",
            "omero.certificates.key": "server.key",
            "omero.certificates.owner": "/L=OMERO/O=OMERO.server",
        }

    def test_config_keep_existing(self, tmpdir):
        (tmpdir / "etc" / "grid").ensure(dir=True)
        omerodir = str(tmpdir)
        configxml = ConfigXml(os.path.join(omerodir, "etc", "grid", "config.xml"))
        configxml["omero.certificates.commonname"] = "omero.example.org"
        configxml["omero.certificates.owner"] = "/L=universe/O=42"
        configxml.close()

        update_config(omerodir)
        cfg = get_config(omerodir)
        cfg.pop("omero.config.version")
        assert cfg == {
            "omero.glacier2.IceSSL.CAs": "server.pem",
            "omero.glacier2.IceSSL.CertFile": "server.p12",
            "omero.glacier2.IceSSL.Ciphers": "HIGH",
            "omero.glacier2.IceSSL.DH.2048": "ffdhe2048.pem",
            "omero.glacier2.IceSSL.DefaultDir": "/OMERO/certs",
            "omero.glacier2.IceSSL.Password": "secret",
            "omero.glacier2.IceSSL.ProtocolVersionMax": "TLS1_3",
            "omero.glacier2.IceSSL.Protocols": "TLS1_2,TLS1_3",
            "omero.certificates.commonname": "omero.example.org",
            "omero.certificates.key": "server.key",
            "omero.certificates.owner": "/L=universe/O=42",
        }

    def test_create_certificates(self, tmpdir):
        (tmpdir / "etc" / "grid").ensure(dir=True)
        omerodir = str(tmpdir)
        datadir = str(tmpdir / "OMERO")
        configxml = ConfigXml(os.path.join(omerodir, "etc", "grid", "config.xml"))
        configxml["omero.data.dir"] = datadir
        configxml.close()

        m = create_certificates(omerodir)
        assert m.startswith("certificates created: ")

        cfg = get_config(omerodir)
        assert cfg["omero.glacier2.IceSSL.DefaultDir"] == os.path.join(datadir, "certs")

        for filename in ("server.key", "server.p12", "server.pem", "ffdhe2048.pem"):
            assert os.path.isfile(os.path.join(datadir, "certs", filename))

        with open(os.path.join(datadir, "certs", "ffdhe2048.pem")) as pem:
            assert (
                sha256(pem.read().encode("ascii")).hexdigest()
                == "2ef7758563185ad0dc1dbc38ab3a91647701e3ebee344fcf86b52e643bacb721"
            )

        out = subprocess.check_output(
            [
                "openssl",
                "pkcs12",
                "-in",
                os.path.join(datadir, "certs", "server.p12"),
                "-passin",
                "pass:secret",
                "-passout",
                "pass:secret",
            ]
        )
        out = out.decode().splitlines()
        for line in (
            "subject=L = OMERO, O = OMERO.server, CN = localhost",
            "issuer=L = OMERO, O = OMERO.server, CN = localhost",
            "-----BEGIN CERTIFICATE-----",
            "-----END CERTIFICATE-----",
            "-----BEGIN ENCRYPTED PRIVATE KEY-----",
            "-----END ENCRYPTED PRIVATE KEY-----",
        ):
            assert line in out

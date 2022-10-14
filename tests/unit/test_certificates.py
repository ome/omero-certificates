import os

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.hazmat.primitives.serialization.pkcs12 import (
    PKCS12Certificate,
    load_pkcs12,
)
from cryptography.x509.oid import NameOID
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
            "omero.glacier2.IceSSL.DefaultDir": "/OMERO/certs",
            "omero.glacier2.IceSSL.Password": "secret",
            "omero.glacier2.IceSSL.ProtocolVersionMax": "TLS1_2",
            "omero.glacier2.IceSSL.Protocols": "TLS1_0,TLS1_1,TLS1_2",
            "omero.certificates.commonname": "localhost",
            "omero.certificates.key": "server.key",
            "omero.certificates.owner": "L=OMERO,O=OMERO.server",
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
            "omero.glacier2.IceSSL.DefaultDir": "/OMERO/certs",
            "omero.glacier2.IceSSL.Password": "secret",
            "omero.glacier2.IceSSL.ProtocolVersionMax": "TLS1_2",
            "omero.glacier2.IceSSL.Protocols": "TLS1_0,TLS1_1,TLS1_2",
            "omero.certificates.commonname": "omero.example.org",
            "omero.certificates.key": "server.key",
            "omero.certificates.owner": "/L=universe/O=42",
        }

    def assert_pkcs12(self, f):
        p12 = load_pkcs12(f.read(), b"secret")
        assert p12.key
        assert isinstance(p12.key, RSAPrivateKey)
        assert p12.key.key_size == 2048

        assert p12.cert
        assert isinstance(p12.cert, PKCS12Certificate)
        certificate = p12.cert.certificate
        assert certificate
        assert isinstance(certificate, x509.Certificate)
        subject = certificate.subject
        assert len(subject) == 3
        (cn,) = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        assert cn.value == "localhost"
        (l,) = subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)
        assert l.value == "OMERO"
        (o,) = subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)
        assert o.value == "OMERO.server"

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

        for filename in ("server.key", "server.p12", "server.pem"):
            assert os.path.isfile(os.path.join(datadir, "certs", filename))

        with open(os.path.join(datadir, "certs", "server.p12"), "rb") as f:
            self.assert_pkcs12(f)

    def test_create_certificates_from_existing_0_2_0(self, tmpdir):
        (tmpdir / "etc" / "grid").ensure(dir=True)
        omerodir = str(tmpdir)
        datadir = str(tmpdir / "OMERO")
        configxml = ConfigXml(os.path.join(omerodir, "etc", "grid", "config.xml"))
        configxml["omero.data.dir"] = datadir
        configxml["omero.certificates.owner"] = "/L=OMERO/O=OMERO.server"
        configxml.close()

        m = create_certificates(omerodir)
        assert m.startswith("certificates created: ")

        cfg = get_config(omerodir)
        assert cfg["omero.glacier2.IceSSL.DefaultDir"] == os.path.join(datadir, "certs")

        for filename in ("server.key", "server.p12", "server.pem"):
            assert os.path.isfile(os.path.join(datadir, "certs", filename))

        with open(os.path.join(datadir, "certs", "server.p12"), "rb") as f:
            self.assert_pkcs12(f)

# type: ignore
# pylint: disable=missing-function-docstring,unnecessary-comprehension,missing-function-docstring
import os
import sqlite3
from datetime import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from fastapi import FastAPI
from fastapi import HTTPException

# import OpenSSL

# Create the SQLite database and table
# ====================================
conn = sqlite3.connect("certificates.db")
cursor = conn.cursor()
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS certificate_client (
        serial_number TEXT PRIMARY KEY,
        certificate TEXT NOT NULL
    )
    """
)
conn.commit()

# Create the FastAPI application and endpoints
# ============================================
app = FastAPI()


@app.get("/certs/server")
def read_server_certificates():
    cert_path = "/etc/ssl/certs/"
    cert_files = os.listdir(cert_path)
    certificates = {}
    for cert_file in cert_files:
        with open(cert_path + cert_file, "rb") as file:
            cert_data = file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            serial_number = cert.serial_number
            certificates[serial_number] = cert_data.decode("utf-8")
    return certificates


@app.get("/certs/server/{serial_number}")
def read_server_certificate(serial_number: int):
    cert_path = "/etc/ssl/certs/"
    cert_files = os.listdir(cert_path)
    for cert_file in cert_files:
        with open(cert_path + cert_file, "rb") as file:
            cert_data = file.read()
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            if cert.serial_number == serial_number:
                return cert_data.decode("utf-8")
    return {"error": "Certificate not found"}, 404


@app.post("/certs/client")
def create_client_certificate(certificate: dict):
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, certificate["country_name"]),
            x509.NameAttribute(
                NameOID.ORGANIZATION_NAME, certificate["organization_name"]
            ),
            x509.NameAttribute(NameOID.COMMON_NAME, certificate["common_name"]),
        ]
    )
    issuer = x509.Name(
        [
            x509.NameAttribute(
                NameOID.COUNTRY_NAME, certificate["issuer"]["country_name"]
            ),
            x509.NameAttribute(
                NameOID.ORGANIZATION_NAME, certificate["issuer"]["organization_name"]
            ),
            x509.NameAttribute(
                NameOID.COMMON_NAME, certificate["issuer"]["common_name"]
            ),
        ]
    )
    public_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048
    ).public_key()
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(
            datetime.datetime.strptime(
                certificate["validity"]["not_before"], "%Y-%m-%dT%H:%M:%SZ"
            )
        )
        .not_valid_after(
            datetime.datetime.strptime(
                certificate["validity"]["not_after"], "%Y-%m-%dT%H:%M:%SZ"
            )
        )
    )
    for extension in certificate["extensions"]:
        builder = builder.add_extension(
            x509.Extension(
                extension["oid"],
                critical=extension["critical"],
                value=extension["value"].encode("utf-8"),
            ),
            critical=extension["critical"],
        )
    cert = builder.sign(
        private_key=rsa.generate_private_key(public_exponent=65537, key_size=2048),
        algorithm=hashes.SHA256(),
        backend=default_backend(),
    )
    return cert.public_bytes(encoding=serialization.Encoding.PEM)


@app.get("/certs/client")
def read_client_certificates():
    # Retrieve the certificates from the SQLite database
    cursor.execute(
        """
        SELECT serial_number, certificate
        FROM certificate_client
        """
    )
    certificates = cursor.fetchall()
    # Return the certificates in a dictionary format
    return {serial_number: certificate for serial_number, certificate in certificates}


@app.get("/certs/client/{serial_number}")
def read_client_certificate(serial_number: str):
    # Retrieve the certificate from the SQLite database
    cursor.execute(
        """
        SELECT certificate
        FROM certificate_client
        WHERE serial_number = ?
        """,
        (serial_number,),
    )
    certificate = cursor.fetchone()
    if certificate is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    # Return the certificate in a dictionary format
    return {"certificate": certificate[0]}

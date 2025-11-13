import os
import uuid
import base64
import cbor2
import requests
from typing import Tuple
from datetime import datetime, timezone
from pydantic import BaseModel
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ObjectIdentifier
from pyasn1.codec.der import decoder
from pyasn1.type import univ, char

from .user_service import UserService
from resource import AppleRootCA


class SecurityService:
    APPLE_APPATTEST_OID = ObjectIdentifier("1.2.840.113635.100.8.2")
    APPLE_ROOT_CERT = None # TODO Placeholder for Apple Root Certificate
    # APPLE_ROOT_CERT = x509.load_pem_x509_certificate(
    #     requests.get(os.getenv("APPLE_ROOT_CA_URL")).content, default_backend()
    # )

    class AttestationRequest(BaseModel):
        key_id: str
        attestation: str
        data: str


    class UserCredentials(BaseModel):
        user_uuid: str
        mfa_code: str


    def __init__(self, session):
        self.session = session

    def create_new_user_token(self) -> str:
        user_id = str(uuid.uuid4())
        token = f"{user_id}.{int(datetime.now(timezone.utc).timestamp())}"
        return token
    

    def attest_request(self, request: AttestationRequest) -> Tuple[bool, str]:
        ''' Validate the attestation request from Apple App Attest.
        Returns a tuple of (is_valid: bool, jwt: str)
        '''
        attestation_bytes = base64.b64decode(request.attestation)

        att_obj = cbor2.loads(attestation_bytes)

        # 3️⃣ Ensure it's the right format
        fmt = att_obj.get("fmt")
        if fmt != "apple-appattest":
            raise ValueError(f"Unexpected format: {fmt}")

        att_stmt = att_obj["attStmt"]
        auth_data = att_obj["authData"]

        # 4️⃣ Extract the certificate chain (x5c)
        x5c_list = att_stmt.get("x5c")
        if not x5c_list:
            raise ValueError("No x5c certificates in attestation")

        # Each item in x5c is a DER-encoded certificate
        certs = [
            x509.load_der_x509_certificate(der, default_backend())
            for der in x5c_list
        ]

        cert_chain = [x509.load_der_x509_certificate(der, default_backend())
              for der in x5c_list]

        if self.verify_certificate_chain(cert_chain):
            cert = cert_chain[0]  # Leaf certificate

            pem_data = cert.public_bytes(encoding=serialization.Encoding.PEM)
            pem_string = pem_data.decode('utf-8')
            print(f"Leaf Certificate PEM:\n{pem_string}")

            # check for team id and bundle id
            ext = cert.extensions.get_extension_for_oid(SecurityService.APPLE_APPATTEST_OID)
    
            raw_bytes = ext.value.value  # This is ASN.1-encoded data (DER sequence)

            seq, _ = decoder.decode(raw_bytes, asn1Spec=univ.Sequence())

            team_id_bytes = seq[0].asOctets()
            team_id_hex = team_id_bytes.hex() 

            # bundle_id_bytes = seq[1].asOctets()
            # try:
            #     bundle_id_str = bundle_id_bytes.decode("utf-8")  # may work if Apple used UTF-8
            # except UnicodeDecodeError:
            #     bundle_id_str = bundle_id_bytes.hex()  # fallback as hex string

            # TODO check team_id and bundle_id values

            # validate the authData including the data and the hash

            parts = request.data.rsplit(".", 1)  # split from the right, once
            uuid = parts[0]
            number = parts[1]
            # TODO compare the hashes and also check timestamp validity
            # TODO return a jwt token instead of uuid
            return True, uuid

        return (False, "")
    

    def assert_request(self, request: AttestationRequest) -> Tuple[bool, str]:
        '''
        Validate the assertion request from Apple App Attest.
        No need to check cert again?
        Returns a tuple of (is_valid: bool, jwt: str)
        '''
        # TODO implement assertion logic
        return (False, "")
    

    def validate_user_credentials(self, credentials: UserCredentials) -> bool:
        # validate the user
        return False
    

    def verify_certificate_chain(self, x5c_list: list[x509.Certificate]):
        try:                
            # x5c_list[0] = leaf, [1] = intermediate, [2] = root (sometimes omitted)
            leaf = x5c_list[0]
            intermediate = x5c_list[1]

            # 1️⃣ Verify leaf was signed by intermediate
            intermediate_public_key = intermediate.public_key()
            intermediate_public_key.verify(
                leaf.signature,
                leaf.tbs_certificate_bytes,
                ec.ECDSA(leaf.signature_hash_algorithm)
            )

            # 2️⃣ Verify intermediate was signed by Apple’s Root CA
            apple_pubkey = AppleRootCA.get_root_cert().public_key()
            apple_pubkey.verify(
                intermediate.signature,
                intermediate.tbs_certificate_bytes,
                ec.ECDSA(intermediate.signature_hash_algorithm)
            )

            # 3️⃣ Optionally check validity dates
            leaf.public_key()  # Extract to use for assertion verification later
            print("✅ Certificate chain verified to Apple root.")
            return True
        except Exception as e:
            print(f"❌ Certificate chain verification failed: {e}")
            return False
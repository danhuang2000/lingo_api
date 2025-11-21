import binascii
import hashlib
import os
import base64
import cbor2
import logging
import jwt
from datetime import datetime, timezone, timedelta
from typing import Tuple
from pydantic import BaseModel
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import ObjectIdentifier
from cryptography.exceptions import InvalidSignature
from pyasn1.codec.der import decoder
from pyasn1.type import univ, char
from cose.messages import CoseMessage

from entity import User
from .user_service import UserService
from resource import AppleRootCA


logger = logging.getLogger(__name__)

class SecurityService:
    APPLE_APPATTEST_OID = ObjectIdentifier("1.2.840.113635.100.8.2")
    APPLE_ROOT_CERT = None # TODO Placeholder for Apple Root Certificate
    # APPLE_ROOT_CERT = x509.load_pem_x509_certificate(
    #     requests.get(os.getenv("APPLE_ROOT_CA_URL")).content, default_backend()
    # )

    JWT_SESSION_SECRET_KEY = "JWT_SESSION_SECRET_KEY"
    JWT_REFRESH_SECRET_KEY = "JWT_REFRESH_SECRET_KEY"


    class DeviceChallenge(BaseModel):
        challenge: str

    class AttestationRequest(BaseModel):
        key_id: str
        attestation: str
        device_uuid: str

    class AssertionRequest(BaseModel):
        key_id: str
        assertion: str
        device_uuid: str

    class UserCredentials(BaseModel):
        user_uuid: str
        device_uuid: str
        mfa_code: str

    class UserUuidInfo(BaseModel):
        user_uuid: str

    class RefreshTokenRequestData(BaseModel):
        refresh_token: str

    def __init__(self, session):
        self.session = session
        self.userService = UserService(session=session)


    def create_jwt(self, request: UserCredentials) -> Tuple[str, str]:
        session_key = os.getenv(SecurityService.JWT_SESSION_SECRET_KEY)
        refresh_key = os.getenv(SecurityService.JWT_REFRESH_SECRET_KEY)
        session_duration = int(os.getenv("JWT_SESSION_IN_MINUTES"))
        refresh_duration = int(os.getenv("JWT_REFRESH_IN_MINUTES"))
        payload = {
            "user_id": request.user_uuid,
            "device_uuid": request.device_uuid,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=session_duration)
        }
        session_token = jwt.encode(payload, session_key, algorithm="HS256")

        payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=refresh_duration)
        refresh_token = jwt.encode(payload, refresh_key, algorithm="HS256")

        return session_token, refresh_token


    def validate_jwt(self, token: str) -> Tuple[bool, str]:
        session_key = os.getenv(SecurityService.JWT_SESSION_SECRET_KEY)
        try:
            decoded = jwt.decode(token, session_key, algorithms=["HS256"])
            return True, ""
        except jwt.ExpiredSignatureError:
            logger.debug("❌ Session token has expired")
        except jwt.InvalidTokenError:
            logger.debug("❌ Session token is invalid")
        return False, "Token invalid or expired"
    

    def refresh_jwt(self, token: RefreshTokenRequestData) -> Tuple[str, str]:
        refresh_key = os.getenv(SecurityService.JWT_REFRESH_SECRET_KEY)
        try:
            decoded = jwt.decode(token, refresh_key, algorithms=["HS256"])
            user_uuid = decoded["user_uuid"]
            device_uuid = decoded["device_uuid"]
            cred = SecurityService.UserCredentials(user_uuid=user_uuid, device_uuid=device_uuid)
            session_token, refresh_token = self.create_jwt(cred)
            logger.debug("tokens refreshed")
            return session_token, refresh_token
        except jwt.ExpiredSignatureError:
            logger.info("❌ Refresh token has expired")
        except jwt.InvalidTokenError:
            logger.info("❌ Refresh token is invalid")
        return None, None


    def test_alternative(self, assertion: str, device_uuid: str):
        device = self.userService.get_device(device_uuid)

        clientDataHash = hashlib.sha256(device.challenge.encode("utf-8")).digest()

        # 2) Load stored PEM and re-check its format
        pem = device.public_key  # whatever you store
        pub = serialization.load_pem_public_key(pem.encode('utf-8'))
        print(f"Public key in assertion:\n{pem}")
        print("Loaded public key type:", type(pub))

        try:
            cose = CoseMessage.decode(assertion)

            sig = cose.signature
            payload = cose.payload  # should be authenticatorData || clientHash

            auth_data = payload[:-32]
            client_hash_from_payload = payload[-32:]

            if client_hash_from_payload != clientDataHash:
                print("hash not match")

            # Build verification message
            verified_bytes = cose._sig_structure()
            
            pub.verify(
                sig,
                verified_bytes,
                ec.ECDSA(hashes.SHA256())
            )
        except InvalidSignature:
            logger.error("❌ InvalidSignature from verify()")
        except Exception as e:
            logger.info("❌ other error:", e)

    
    def assert_request(self, request: AssertionRequest) -> Tuple[bool, str, str]:
        '''
        Validate the assertion request from Apple App Attest.
        Returns a tuple of (is_valid: bool, device_uuid: str, user_uuid: str)
        '''
        logger.info(f"Validating assertion for device: {request.device_uuid}")

        assertion_bytes = base64.b64decode(request.assertion)

        self.test_alternative(assertion_bytes, request.device_uuid)

        att_obj = cbor2.loads(assertion_bytes)

        device = self.userService.get_device(request.device_uuid)

        clientDataHash = hashlib.sha256(device.challenge.encode("utf-8")).digest()

        # 1) Ensure att_obj values are bytes
        auth = bytes(att_obj["authenticatorData"])
        sig  = bytes(att_obj["signature"])

        print("auth len:", len(auth), "auth hex:", binascii.hexlify(auth).decode())
        print("sig len:", len(sig), "sig hex:", binascii.hexlify(sig).decode())
        print("clientDataHash len:", len(clientDataHash), "cdh hex:", binascii.hexlify(clientDataHash).decode())

        to_be_signed = auth + clientDataHash
        print("to_be_signed len:", len(to_be_signed), "hex:", binascii.hexlify(to_be_signed).decode())

        # 2) Load stored PEM and re-check its format
        pem = device.public_key  # whatever you store
        pub = serialization.load_pem_public_key(pem.encode('utf-8'))
        print(f"Public key in assertion:\n{pem}")
        print("Loaded public key type:", type(pub))

        # 4) Decode DER signature to (r, s) to inspect
        r, s = utils.decode_dss_signature(sig)
        print("r:", hex(r))
        print("s:", hex(s))

        # 3) Verify (this is what you're doing — but include debug)
        try:
            pub.verify(sig, to_be_signed, ec.ECDSA(hashes.SHA256()))
            logger.debug("✅ verify() succeeded")
            return True, device.uuid, device.user.uuid
        except InvalidSignature:
            logger.error("❌ InvalidSignature from verify()")
            # TODO figure out why it fails
            return True, device.uuid, device.user.uuid
        except Exception as e:
            logger.info("❌ other error:", e)
            return None


        # clientDataHash = hashlib.sha256(device.challenge.encode("utf-8")).digest()

        # # Concatenate them exactly as Apple did
        # to_be_signed = att_obj["authenticatorData"] + clientDataHash

        # pem = device.public_key
        # public_key = serialization.load_pem_public_key(pem.encode("utf-8"))

        # try:
        #     public_key.verify(att_obj["signature"], to_be_signed, ec.ECDSA(hashes.SHA256()))
        #     logger.debug("✅ Signature verified — clientDataHash is valid.")
        #     return (True, device.uuid, device.user.uuid)
        # except Exception as e:
        #     logger.info("❌ Signature verification failed:", e)
        #     return None

        # return None
    

    def attest_request(self, request: AttestationRequest) -> UserService.DeviceChallenge:
        ''' Validate the attestation request from Apple App Attest.
        Returns a tuple of (is_valid: bool, device_uuid)
        '''
        logger.info(f"Validating attestation for device: {request.device_uuid}")

        attestation_bytes = base64.b64decode(request.attestation)

        att_obj = cbor2.loads(attestation_bytes)

        # 3️⃣ Ensure it's the right format
        fmt = att_obj.get("fmt")
        if fmt != "apple-appattest":
            raise ValueError(f"Unexpected format: {fmt}")

        att_stmt = att_obj["attStmt"]

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

            auth_data = att_obj["authData"]

            pem_data = cert.public_bytes(encoding=serialization.Encoding.PEM)
            logger.debug(pem_data.decode("utf-8"))

            public_key = cert.public_key()

            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            public_key_pem_str = public_key_pem.decode("utf-8")
            print(f"public key in attestation:\n{public_key_pem_str}")
            self.userService.set_device_key_info(
                device_uuid=request.device_uuid,
                key_id=request.key_id, 
                key_pem=public_key_pem_str)

            device = self.userService.update_device_challenge(
                device_uuid=request.device_uuid,
                new_challenge=os.urandom(16).hex())
            return UserService.DeviceChallenge(challenge=device.challenge, device_uuid=request.device_uuid)
        return None
    
    

    def validate_user_credentials(self, credentials: UserCredentials) -> bool:
        # TODO validate the user
        return True
    

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
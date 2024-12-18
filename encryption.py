from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from Crypto.Cipher import AES

import os

KEY_VAULT_NAME = os.environ['KEY_VAULT_NAME']
KEY_VAULT_URI  = f'https://{KEY_VAULT_NAME}.vault.azure.net'

AES_MODE = AES.MODE_EAX

def get_evidence_aes_key() -> bytes:
    creds = ManagedIdentityCredential(client_id = os.environ['MANAGED_CLIENT_ID'])

    client = SecretClient(
        vault_url  = KEY_VAULT_URI,
        credential = creds
    )

    hex = client.get_secret(os.environ['SECRET_NAME']).value

    return bytes.fromhex(hex)

def get_db_aes_key() -> bytes:
    creds = ManagedIdentityCredential(client_id = os.environ['MANAGED_CLIENT_ID']) 

    client = SecretClient(
        vault_url  = KEY_VAULT_URI,
        credential = creds
    )

    hex = client.get_secret(os.environ['DB_SECRET_NAME']).value

    return bytes.fromhex(hex)

def encrypt_evidence(content: str):
    key = get_evidence_aes_key()

    return encrypt(content, key)


def encrypt_file_name(content: str):
    key = get_db_aes_key()

    return encrypt(content, key)

def encrypt(content: str, key: bytes):
    data_bytes = bytes(content, "utf-8")

    cipher = AES.new(key, AES_MODE)

    cipher_text, tag = cipher.encrypt_and_digest(data_bytes)
    nonce = cipher.nonce

    cipher_text_hex = bytes.hex(cipher_text)
    tag_hex         = bytes.hex(tag)
    nonce_hex       = bytes.hex(nonce)

    result = f'{tag_hex}{nonce_hex}{cipher_text_hex}'

    return result
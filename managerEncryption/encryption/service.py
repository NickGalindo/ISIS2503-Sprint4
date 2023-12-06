from manager.load_config import CONFIG

from typing import Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets
import base64

def encrypt(data: Dict) -> Dict:
    for key in data:
        noonce = secrets.token_bytes(12)
        val_encrypted = noonce + AESGCM(base64.b64decode(CONFIG["PAYLOAD_KEY"])).encrypt(noonce, data[key].encode(), b"")
        data[key] = base64.b64encode(val_encrypted).decode("utf-8")

    return data

def decrypt(data: Dict) -> Dict:
    for key in data:
        val_encoded = base64.b64decode(data[key].encode("UTF-8"))
        data[key] = AESGCM(base64.b64decode(CONFIG["PAYLOAD_KEY"])).decrypt(val_encoded[:12], val_encoded[12:], b"").decode()

    return data

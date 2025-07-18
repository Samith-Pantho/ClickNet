import base64
import hashlib
import random
import string
import argparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from pydantic import BaseModel

# Fixed encryption key (provided by you)
g_fixed_key = "LES3fT8RMAgOUpphi5ecDL6FCgfgnv95IxNIZaUk0QEfDtVKvXzG"

# Mock logger (replace with real one)
class SystemLogErrorSchema(BaseModel):
    Msg: str
    Type: str
    ModuleName: str
    CreatedBy: str

def AddLogOrError(log: SystemLogErrorSchema):
    print(f"[{log.Type}] {log.ModuleName}: {log.Msg}")

def _GenerateRandomString(length: int = 32) -> str:
    try:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_GenerateRandomString",
            CreatedBy = ""
        ))
        raise

def _AES_Encrypt(plain_text: str, key: bytes) -> str:
    try:
        if len(key) not in (16, 24, 32):
            raise ValueError(f"Invalid AES key length: {len(key)} bytes")
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(plain_text.encode('utf-16le'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode()
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_AES_Encrypt",
            CreatedBy = ""
        ))
        raise

def _AES_Decrypt(encrypted_text: str, key: bytes) -> str:
    try:
        if len(key) not in (16, 24, 32):
            raise ValueError(f"Invalid AES key length: {len(key)} bytes")
        decoded = base64.b64decode(encrypted_text)
        iv = decoded[:16]
        cipher_text = decoded[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(cipher_text), AES.block_size)
        return decrypted.decode('utf-16le')
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/_AES_Decrypt",
            CreatedBy = ""
        ))
        raise

def _DeriveAESKey(key_str: str, length=32) -> bytes:
    return hashlib.sha256(key_str.encode('utf-8')).digest()[:length]

def GetEncryptedText(plain_text: str) -> str:
    try:
        random_key_str = _GenerateRandomString()
        random_key = _DeriveAESKey(random_key_str)
        fixed_key = _DeriveAESKey(g_fixed_key)

        e_text = _AES_Encrypt(plain_text, random_key)
        e_key = _AES_Encrypt(random_key_str, fixed_key)

        return base64.b64encode(f"{e_key}::{e_text}".encode()).decode()
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/GetEncryptedText",
            CreatedBy = ""
        ))
        raise

def GetDecryptedText(encrypted_text: str) -> str:
    try:
        if encrypted_text:
            decoded = base64.b64decode(encrypted_text).decode()
            e_key, e_text = decoded.split('::', 1)

            fixed_key = _DeriveAESKey(g_fixed_key)
            plain_random_key = _AES_Decrypt(e_key, fixed_key)
            random_key = _DeriveAESKey(plain_random_key)

            return _AES_Decrypt(e_text, random_key)
        return ''
    except Exception as ex:
        AddLogOrError(SystemLogErrorSchema(
            Msg = str(ex),
            Type = "ERROR",
            ModuleName = "CommonServices/GetDecryptedText",
            CreatedBy = ""
        ))
        raise

# ------------------------------
# Command-line entry point
# ------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a string using AES")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-e", "--encrypt", help="Encrypt the given string")
    group.add_argument("-d", "--decrypt", help="Decrypt the given encrypted string")

    args = parser.parse_args()

    if args.encrypt:
        try:
            print(GetEncryptedText(args.encrypt))
        except Exception as e:
            print("Encryption failed:", e)
    elif args.decrypt:
        try:
            print(GetDecryptedText(args.decrypt))
        except Exception as e:
            print("Decryption failed:", e)

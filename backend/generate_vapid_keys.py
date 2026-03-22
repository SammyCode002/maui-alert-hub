"""
One-time VAPID key generation for Web Push notifications.

Run this ONCE and add the output to your environment variables:

  Render (backend):
    VAPID_PRIVATE_KEY = <private key>
    VAPID_PUBLIC_KEY  = <public key>

  Vercel (frontend):
    VITE_VAPID_PUBLIC_KEY = <public key>  (same public key)

Usage:
    cd backend
    py generate_vapid_keys.py
"""

import base64
from py_vapid import Vapid
from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, PublicFormat, NoEncryption
)

vapid = Vapid()
vapid.generate_keys()

priv_der = vapid._private_key.private_bytes(
    encoding=Encoding.DER,
    format=PrivateFormat.PKCS8,
    encryption_algorithm=NoEncryption(),
)
private_key = base64.urlsafe_b64encode(priv_der).decode().rstrip("=")

pub_raw = vapid._public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
public_key = base64.urlsafe_b64encode(pub_raw).decode().rstrip("=")

print("=" * 60)
print("VAPID Keys Generated — add these to your env vars")
print("=" * 60)
print(f"\nVAPID_PRIVATE_KEY={private_key}")
print(f"\nVAPID_PUBLIC_KEY={public_key}")
print(f"\nVITE_VAPID_PUBLIC_KEY={public_key}  (same, goes in Vercel)")
print("\n" + "=" * 60)
print("Keep the PRIVATE key secret. The PUBLIC key is safe to expose.")

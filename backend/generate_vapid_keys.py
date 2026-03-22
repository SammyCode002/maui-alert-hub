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

from py_vapid import Vapid

vapid = Vapid()
vapid.generate_keys()

private_key = vapid.private_key_urlsafe
public_key = vapid.public_key_urlsafe

print("=" * 60)
print("VAPID Keys Generated — add these to your env vars")
print("=" * 60)
print(f"\nVAPID_PRIVATE_KEY={private_key}")
print(f"\nVAPID_PUBLIC_KEY={public_key}")
print(f"\nVITE_VAPID_PUBLIC_KEY={public_key}  (same, goes in Vercel)")
print("\n" + "=" * 60)
print("Keep the PRIVATE key secret. The PUBLIC key is safe to expose.")

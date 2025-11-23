#!/usr/bin/env python3
"""
Generate VAPID keys for Web Push notifications.
Run this script to generate the keys needed for push notifications.
"""

import os
import sys

try:
    from py_vapid import Vapid01, Vapid02
    VAPID_AVAILABLE = True
except ImportError:
    VAPID_AVAILABLE = False
    print("Warning: py-vapid not available. Install with: pip install py-vapid")

def generate_vapid_keys():
    """Generate VAPID keys for push notifications."""
    if not VAPID_AVAILABLE:
        print("Error: py-vapid or pywebpush is required to generate VAPID keys.")
        print("Install with: pip install py-vapid pywebpush")
        return None
    
    try:
        if 'USE_PYWEBPUSH' in globals() and USE_PYWEBPUSH:
            # Use pywebpush to generate keys
            from pywebpush import WebPusher
            import base64
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.primitives import serialization
            
            # Generate EC key pair
            private_key = ec.generate_private_key(ec.SECP256R1())
            public_key = private_key.public_key()
            
            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Get public key in uncompressed point format for base64
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            
            public_key_base64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
            
            return {
                'private_key': private_pem.decode('utf-8'),
                'public_key': public_pem.decode('utf-8'),
                'public_key_base64': public_key_base64
            }
        else:
            # Use py-vapid
            vapid = Vapid02()
            vapid.generate_keys()
            
            private_key = vapid.private_key.pem
            public_key = vapid.public_key.pem
            
            # Extract the public key in base64 URL-safe format (for frontend)
            import base64
            from cryptography.hazmat.primitives import serialization
            
            # Get public key bytes
            public_key_bytes = vapid.public_key.public_key().public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )
            
            # Convert to base64 URL-safe
            public_key_base64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
            
            return {
                'private_key': private_key,
                'public_key': public_key,
                'public_key_base64': public_key_base64
            }
    except Exception as e:
        print(f"Error generating VAPID keys: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_keys_to_env_file(keys, email="admin@leadintelligence.com"):
    """Save VAPID keys to .env file."""
    env_file = ".env"
    env_example_file = ".env.example"
    
    # Read existing .env if it exists
    env_vars = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Update with VAPID keys
    env_vars['VAPID_PRIVATE_KEY'] = keys['private_key'].replace('\n', '\\n')
    env_vars['VAPID_PUBLIC_KEY'] = keys['public_key'].replace('\n', '\\n')
    env_vars['VAPID_EMAIL'] = email
    env_vars['NEXT_PUBLIC_VAPID_PUBLIC_KEY'] = keys['public_key_base64']
    
    # Write to .env
    with open(env_file, 'w') as f:
        f.write("# VAPID Keys for Web Push Notifications\n")
        f.write("# Generated automatically - DO NOT commit to version control\n\n")
        f.write(f"VAPID_PRIVATE_KEY={env_vars['VAPID_PRIVATE_KEY']}\n")
        f.write(f"VAPID_PUBLIC_KEY={env_vars['VAPID_PUBLIC_KEY']}\n")
        f.write(f"VAPID_EMAIL={env_vars['VAPID_EMAIL']}\n")
        f.write(f"NEXT_PUBLIC_VAPID_PUBLIC_KEY={env_vars['NEXT_PUBLIC_VAPID_PUBLIC_KEY']}\n\n")
        
        # Write other existing vars
        for key, value in env_vars.items():
            if not key.startswith('VAPID') and key != 'NEXT_PUBLIC_VAPID_PUBLIC_KEY':
                f.write(f"{key}={value}\n")
    
    # Update .env.example (without actual keys)
    if not os.path.exists(env_example_file):
        with open(env_example_file, 'w') as f:
            f.write("# VAPID Keys for Web Push Notifications\n")
            f.write("# Generate keys using: python scripts/generate_vapid_keys.py\n\n")
            f.write("VAPID_PRIVATE_KEY=your_private_key_here\n")
            f.write("VAPID_PUBLIC_KEY=your_public_key_here\n")
            f.write("VAPID_EMAIL=admin@leadintelligence.com\n")
            f.write("NEXT_PUBLIC_VAPID_PUBLIC_KEY=your_public_key_base64_here\n")
    
    print(f"✅ VAPID keys saved to {env_file}")
    print(f"📝 Example file updated: {env_example_file}")

def main():
    """Main function to generate and save VAPID keys."""
    print("🔑 Generating VAPID keys for Web Push notifications...\n")
    
    keys = generate_vapid_keys()
    if not keys:
        print("\n❌ Failed to generate VAPID keys.")
        sys.exit(1)
    
    print("✅ VAPID keys generated successfully!\n")
    print("Private Key (first 50 chars):", keys['private_key'][:50] + "...")
    print("Public Key (first 50 chars):", keys['public_key'][:50] + "...")
    print("Public Key (Base64):", keys['public_key_base64'][:50] + "...\n")
    
    # Ask for email
    email = input("Enter email for VAPID (default: admin@leadintelligence.com): ").strip()
    if not email:
        email = "admin@leadintelligence.com"
    
    # Save to .env
    save_keys_to_env_file(keys, email)
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Review the .env file to ensure keys are correct")
    print("2. Restart your backend server to load the new keys")
    print("3. Restart your frontend dev server to load NEXT_PUBLIC_VAPID_PUBLIC_KEY")
    print("4. Test push notifications in the UI")

if __name__ == "__main__":
    main()


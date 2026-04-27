import os
import sys
import json
import struct
import subprocess
import platform
from pathlib import Path

HOST_NAME = "com.dbsc.local_messenger"
EXTENSION_ID = "@addon-example" # Must match the ID in your manifest.json

# ---------------------------------------------------------
# Installation & Verification Logic
# ---------------------------------------------------------
def ensure_installed(verbose=False):
    """Checks if registry/manifest are configured, and installs them if missing."""
    is_compiled = getattr(sys, 'frozen', False)
    
    # When running as a compiled executable, sys.executable points to the .exe itself.
    if is_compiled:
        executable_path = Path(sys.executable).resolve()
    else:
        executable_path = Path(__file__).resolve()

    current_dir = executable_path.parent
    manifest_path = current_dir / f"{HOST_NAME}.json"
    needs_install = False

    # 1. Check if the manifest exists and points to this exact executable
    if not manifest_path.exists():
        needs_install = True
    else:
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
                if manifest.get("path") != str(executable_path):
                    needs_install = True
        except Exception:
            needs_install = True

    # 2. Check if the OS registry/symlink exists and points to our manifest
    if sys.platform.startswith('win'):
        import winreg
        registry_path = rf"Software\Mozilla\NativeMessagingHosts\{HOST_NAME}"
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if val != str(manifest_path):
                needs_install = True
        except Exception:
            needs_install = True
    else:
        if sys.platform.startswith('darwin'):
            target_path = Path.home() / f"Library/Application Support/Mozilla/NativeMessagingHosts/{HOST_NAME}.json"
        else:
            target_path = Path.home() / f".mozilla/native-messaging-hosts/{HOST_NAME}.json"
            
        if not target_path.exists() or not target_path.is_symlink() or os.readlink(target_path) != str(manifest_path):
            needs_install = True

    if not needs_install:
        if verbose:
            print("Middleware is already correctly installed and registered.")
        return

    if verbose:
        print("Installing and registering middleware...")

    # --- Proceed with Installation ---
    manifest = {
        "name": HOST_NAME,
        "description": "Device-Bound Session Credentials TPM Middleware",
        "path": str(executable_path),
        "type": "stdio",
        "allowed_extensions": [EXTENSION_ID]
    }
    
    try:
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        if verbose: print(f"Created manifest file at: {manifest_path}")
    except Exception as e:
        if verbose: print(f"[ERROR] Failed to write manifest file: {e}")
        if verbose: sys.exit(1)
        return # Fail silently if launched by Firefox and lacking permissions

    if sys.platform.startswith('win'):
        import winreg
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
            winreg.CloseKey(key)
            if verbose: print(f"Successfully registered host in Windows Registry: HKCU\\{registry_path}")
        except Exception as e:
            if verbose: print(f"[ERROR] Failed to write to registry: {e}")
            if verbose: sys.exit(1)
    else:
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            if target_path.exists(): target_path.unlink()
            target_path.symlink_to(manifest_path)
            if verbose: print(f"Successfully registered host for {sys.platform} at: {target_path}")
        except Exception as e:
            if verbose: print(f"[ERROR] Failed to register host: {e}")
            if verbose: sys.exit(1)

    if not sys.platform.startswith('win') and not getattr(sys, 'frozen', False):
        os.chmod(executable_path, 0o755)

    if verbose:
        print("\nInstallation complete! You can now use the DBSC extension in Firefox.")

# ---------------------------------------------------------
# Firefox Native Messaging Protocol Implementation
# ---------------------------------------------------------
def get_message():
    """Reads a message from standard input (Firefox)."""
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        sys.exit(0)
    
    # Unpack the 32-bit integer length
    message_length = struct.unpack('@I', raw_length)[0]
    
    # Read the JSON message based on the length
    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def send_message(message_content):
    """Sends a message to standard output (Firefox)."""
    encoded_content = json.dumps(message_content).encode('utf-8')
    
    # Pack the length of the message into a 32-bit integer
    encoded_length = struct.pack('@I', len(encoded_content))
    
    # Send the length followed by the message
    sys.stdout.buffer.write(encoded_length)
    sys.stdout.buffer.write(encoded_content)
    sys.stdout.buffer.flush()

# ---------------------------------------------------------
# TPM Interaction Logic
# ---------------------------------------------------------
def sign_with_tpm(challenge_data):
    """
    Simulates or performs the actual TPM signing process.
    In a real implementation, you would use a cryptographic library 
    (like cryptography or PyKCS11) or call out to tpm2-tools.
    """
    try:
        # --- REAL TPM IMPLEMENTATION EXAMPLE (using tpm2-tools) ---
        # 1. Write the challenge to a file
        # with open("challenge.dat", "w") as f: f.write(challenge_data)
        # 2. Call the TPM to sign it
        # subprocess.run(["tpm2_sign", "-c", "key.ctx", "-g", "sha256", "-m", "challenge.dat", "-s", "signature.dat"], check=True)
        # 3. Read the signature back
        # with open("signature.dat", "rb") as f: return f.read().hex()
        
        # --- MOCK IMPLEMENTATION FOR PROTOTYPING ---
        # We append a mock signature to prove the communication loop works


        #How do I implement real TPM 2.0 signing in `middleware.py` instead of the mock signature?


        mock_signature = f"tpm2_signed_{challenge_data}_with_hw_key"
        return mock_signature
        
    except Exception as e:
        return f"error_signing: {str(e)}"

# ---------------------------------------------------------
# Main Event Loop
# ---------------------------------------------------------
def main():
    # If no arguments are provided, it means a user double-clicked the file.
    if len(sys.argv) == 1:
        ensure_installed(verbose=True)
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to exit...")
        sys.exit(0)
        
    # Otherwise, Firefox launched it. Verify installation silently and run the middleware loop.
    ensure_installed(verbose=False)

    while True:
        msg = get_message()
        
        if msg.get("action") == "encrypt_session":
            data = msg.get("data", {})
            domain = data.get("domain", "unknown_domain")
            challenge = data.get("challenge", "")
            
            # Pass the server's challenge to the TPM to be signed
            bound_token = sign_with_tpm(challenge)
            
            if bound_token.startswith("error_signing:"):
                send_message({"action": "encryption_failed", "domain": domain, "error": bound_token})
            else:
                send_message({"action": "encryption_complete", "domain": domain, "token": bound_token})

if __name__ == '__main__':
    main()
import os
import sys
import json
import platform
from pathlib import Path

HOST_NAME = "com.dbsc.local_messenger"
EXTENSION_ID = "@addon-example" # Must match the ID in your manifest.json

def install_host():
    """Installs the native messaging host for Firefox."""
    
    # 1. Determine absolute paths based on the current directory
    current_dir = Path(__file__).parent.resolve()
    
    if sys.platform.startswith('win'):
        # Windows uses the batch wrapper
        executable_path = current_dir / "run_middleware.bat"
    else:
        # Linux/macOS can run the python script directly (ensure it has executable permissions)
        executable_path = current_dir / "middleware.py"
        os.chmod(executable_path, 0o755)
        
    manifest_path = current_dir / f"{HOST_NAME}.json"

    # 2. Dynamically generate the manifest JSON with absolute paths
    manifest = {
        "name": HOST_NAME,
        "description": "Device-Bound Session Credentials TPM Middleware",
        "path": str(executable_path),
        "type": "stdio",
        "allowed_extensions": [EXTENSION_ID]
    }

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
        
    print(f"Created manifest file at: {manifest_path}")

    # 3. Register the manifest with Firefox based on the OS
    if sys.platform.startswith('win'):
        import winreg
        
        # Write to Windows Registry
        registry_path = rf"Software\Mozilla\NativeMessagingHosts\{HOST_NAME}"
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, registry_path)
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(manifest_path))
            winreg.CloseKey(key)
            print(f"Successfully registered host in Windows Registry: HKCU\\{registry_path}")
        except Exception as e:
            print(f"Failed to write to registry: {e}")
            sys.exit(1)
            
    elif sys.platform.startswith('darwin'):
        # macOS
        target_dir = Path.home() / "Library/Application Support/Mozilla/NativeMessagingHosts"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{HOST_NAME}.json"
        
        # Symlink or copy
        if target_path.exists(): target_path.unlink()
        target_path.symlink_to(manifest_path)
        print(f"Successfully registered host for macOS at: {target_path}")
        
    else:
        # Linux
        target_dir = Path.home() / ".mozilla/native-messaging-hosts"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{HOST_NAME}.json"
        
        # Symlink or copy
        if target_path.exists(): target_path.unlink()
        target_path.symlink_to(manifest_path)
        print(f"Successfully registered host for Linux at: {target_path}")
        
    print("\nInstallation complete! You can now use the DBSC extension in Firefox.")

if __name__ == '__main__':
    install_host()
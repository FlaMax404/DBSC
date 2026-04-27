import os
import sys
from pathlib import Path

HOST_NAME = "com.dbsc.local_messenger"

def uninstall_host():
    """Uninstalls the native messaging host for Firefox."""
    current_dir = Path(__file__).parent.resolve()
    manifest_path = current_dir / f"{HOST_NAME}.json"

    # 1. Remove the local manifest file
    if manifest_path.exists():
        manifest_path.unlink()
        print(f"Removed local manifest file at: {manifest_path}")

    # 2. Remove the registration from Firefox based on the OS
    if sys.platform.startswith('win'):
        import winreg
        registry_path = rf"Software\Mozilla\NativeMessagingHosts\{HOST_NAME}"
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, registry_path)
            print(f"Successfully removed host from Windows Registry: HKCU\\{registry_path}")
        except FileNotFoundError:
            print("Registry key not found. It may have already been removed.")
        except Exception as e:
            print(f"Failed to remove from registry: {e}")
            
    elif sys.platform.startswith('darwin'):
        # macOS
        target_path = Path.home() / f"Library/Application Support/Mozilla/NativeMessagingHosts/{HOST_NAME}.json"
        if target_path.exists():
            target_path.unlink()
            print(f"Successfully removed host for macOS at: {target_path}")
        else:
            print("Host manifest not found in macOS Mozilla directory.")
            
    else:
        # Linux
        target_path = Path.home() / f".mozilla/native-messaging-hosts/{HOST_NAME}.json"
        if target_path.exists():
            target_path.unlink()
            print(f"Successfully removed host for Linux at: {target_path}")
        else:
            print("Host manifest not found in Linux Mozilla directory.")
        
    print("\nUninstallation complete! The DBSC extension can no longer launch the middleware.")

    if getattr(sys, 'frozen', False):
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    uninstall_host()
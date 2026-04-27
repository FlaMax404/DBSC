# Secure-DBSC for Firefox

Secure-DBSC is a Firefox browser extension that implements **Device-Bound Session Credentials (DBSC)**. The primary goal of this project is to prevent session hijacking by cryptographically binding your active web sessions to your device's hardware via TPM 2.0. 

By linking the session to a cryptographic key securely stored on the device, even if a malicious actor manages to steal your session cookies, they will be completely useless on another machine without the corresponding hardware key.

## Project Components
* **Browser Extension:** Intercepts authentication challenges and injects DBSC proofs into outgoing web requests.
* **Native Middleware:** A Python-based messaging host that sits between the Firefox extension and the device's hardware/TPM to sign challenges.

---

## How to Install the Middleware

Because standard web pages and extensions cannot directly access your device's local hardware for security reasons, this extension relies on a **Native Messaging Host** (the middleware) to perform the cryptographic signing. 

Firefox needs to be explicitly told where this middleware is located. You can install and register it using the provided installation script.

### Option 1: Running from Python Source
If you have Python installed on your system:
1. Open your terminal or command prompt.
2. Navigate to the extension's directory:
   ```bash
   cd "extension 1"
   ```
3. Run the installation script:
   ```bash
   python install_host.py
   ```
   *Note: This will generate a `com.dbsc.local_messenger.json` manifest file and automatically configure the necessary Windows Registry keys or macOS/Linux directories so Firefox knows how to launch the middleware.*

### Option 2: Running via Standalone Executable (If Compiled)
The provided standalone executable (`middleware.exe`), Python is not required:
1. Ensure the executable is located in the same folder as the extension files.
2. Double-click the installer executable.
3. A terminal window will briefly appear, execute the registration steps, and display a success message.

### Verifying the Installation
1. Open Firefox and go to `about:debugging`.
2. Click **This Firefox** and load the extension by clicking **Load Temporary Add-on...** and selecting the `manifest.json` file.
3. Click the Secure-DBSC extension icon in your browser toolbar and toggle it to **Enabled**.
4. The popup should report the Middleware status as **🟢 Connected**.

---

## Uninstallation
To completely remove the native messaging host registration from your system, simply run the `uninstall_host.exe` executable. This will delete the generated manifest and remove the registry keys or symlinks.

import sys
import json
import struct
import subprocess

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
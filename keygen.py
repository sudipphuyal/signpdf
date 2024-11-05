from OpenSSL import crypto
import os

# Create the keys directory if it doesn't exist
keys_dir = './keys'
os.makedirs(keys_dir, exist_ok=True)

# Paths to store the keys
private_key_path = os.path.join(keys_dir, 'private.pem')
public_cert_path = os.path.join(keys_dir, 'public.pem')

# Generate a key pair
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)  # RSA key with 2048 bits

# Create a self-signed certificate
cert = crypto.X509()
cert.get_subject().C = "US"  # Country (modify as needed)
cert.get_subject().ST = "California"  # State (modify as needed)
cert.get_subject().L = "San Francisco"  # City (modify as needed)
cert.get_subject().O = "Your Organization"  # Organization (modify as needed)
cert.get_subject().OU = "Your Unit"  # Organizational Unit (modify as needed)
cert.get_subject().CN = "Sudip Phuyal"  # Common Name (modify as needed)
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(10*365*24*60*60)  # Valid for 10 years
cert.set_issuer(cert.get_subject())
cert.set_pubkey(key)
cert.sign(key, 'sha256')

# Write the private key to a file
with open(private_key_path, 'wb') as private_key_file:
    private_key_file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

# Write the public certificate to a file
with open(public_cert_path, 'wb') as public_cert_file:
    public_cert_file.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

print(f"Private key saved to: {private_key_path}")
print(f"Public certificate saved to: {public_cert_path}")

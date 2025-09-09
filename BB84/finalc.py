import numpy as np  

# -------------------------------
# Helper functions
# -------------------------------
def text_to_bits(text):
    """Convert string to bit array"""
    return np.array([int(b) for c in text for b in format(ord(c), '08b')])

def bits_to_text(bits):
    """Convert bit array back to string"""
    return ''.join(chr(int(''.join(map(str, bits[i:i+8])), 2)) 
                   for i in range(0, len(bits), 8))

def otp_encrypt(message_bits, key):
    """Encrypt message using One-Time Pad"""
    key_repeated = np.resize(key, message_bits.shape)
    return np.bitwise_xor(message_bits, key_repeated), key_repeated

def otp_decrypt(cipher_bits, key_repeated):
    """Decrypt cipher using One-Time Pad"""
    return np.bitwise_xor(cipher_bits, key_repeated)

# -------------------------------
# Example: Secure message
# -------------------------------
message = "hello"
print("Original message: ", message)

# Convert text → bits
msg_bits = text_to_bits(message)
print("Message bits:     ", msg_bits)

# Show ASCII values
ascii_vals = [ord(c) for c in message]
print("ASCII values:     ", ascii_vals)

# Shared key (from BB84)
shared_key = [1, 0, 0]   # Demo key
key = np.array(shared_key)

# Encrypt
cipher_bits, key_repeated = otp_encrypt(msg_bits, key)
print("Key (repeated):   ", key_repeated)
print("Cipher bits:      ", cipher_bits)

# Decrypt
decrypted_bits = otp_decrypt(cipher_bits, key_repeated)
decrypted_text = bits_to_text(decrypted_bits)

print("Decrypted bits:   ", decrypted_bits)
print("Decrypted text:   ", decrypted_text)

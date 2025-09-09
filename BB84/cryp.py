import numpy as np

# Shared secret key from BB84
shared_key = [1, 0, 0]

# Convert key to numpy array
key = np.array(shared_key)

# -------------------------------
# Message (as bits)
# Let's send "HI" (ASCII)
# -------------------------------
message = "HI"
msg_bits = ''.join(format(ord(c), '08b') for c in message)  # binary string
msg_bits = np.array([int(b) for b in msg_bits])

print("Original message: ", message)
print("Message bits:     ", msg_bits)

# -------------------------------
# Encryption with One-Time Pad
# -------------------------------
# Repeat key if message is longer
key_repeated = np.resize(key, msg_bits.shape)

cipher_bits = np.bitwise_xor(msg_bits, key_repeated)
print("Cipher bits:      ", cipher_bits)

# -------------------------------
# Decryption with One-Time Pad
# -------------------------------
decrypted_bits = np.bitwise_xor(cipher_bits, key_repeated)

# Convert bits back to text
decrypted_str = ''.join(chr(int(''.join(map(str,decrypted_bits[i:i+8])), 2)) 
                        for i in range(0, len(decrypted_bits), 8))

print("Decrypted bits:   ", decrypted_bits)
print("Decrypted text:   ", decrypted_str)


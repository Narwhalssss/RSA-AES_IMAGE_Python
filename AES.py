from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from PIL import Image
import io
import base64
import time
from memory_profiler import profile
import numpy as np
start_time = time.time()
@profile
def encrypt_image(image_path, key):
    # Read image data
    with open(image_path, 'rb') as file:
        image_data = file.read()

    # Generate a random IV
    iv = get_random_bytes(AES.block_size)

    # Create an AES cipher object in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Pad the image data
    padded_data = pad(image_data, AES.block_size)

    # Encrypt the padded image data
    encrypted_data = cipher.encrypt(padded_data)

    # Combine IV and encrypted data
    result = iv + encrypted_data

    return base64.b64encode(result).decode('utf-8')

@profile
def decrypt_image(encrypted_image_path, key):
    # Base64 decode the input
    encrypted_data = base64.b64decode(encrypted_image_path)

    # Extract IV from the encrypted data
    iv = encrypted_data[:AES.block_size]

    # Create an AES cipher object in CBC mode
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the encrypted data
    decrypted_data = unpad(cipher.decrypt(encrypted_data[AES.block_size:]), AES.block_size)

    # Save the decrypted data to an image file
    with io.BytesIO(decrypted_data) as image_stream:
        decrypted_image = Image.open(image_stream)
        decrypted_image.save('decrypted_image.webp')

# usage
key = get_random_bytes(32)  # 256-bit key
image_path = 'Wow.webp'
print("--- %s seconds ---" % (time.time() - start_time))
# Encrypt the image
encrypted_image = encrypt_image(image_path, key)

# Save the encrypted image data to a file
with open('encrypted_image.txt', 'w') as file:
    file.write(encrypted_image)
print("--- %s seconds ---" % ((time.time() - start_time)))
# Decrypt the image
started_time = time.time()
with open('encrypted_image.txt', 'r') as file:
    encrypted_image_data = file.read()

decrypt_image(encrypted_image_data, key)
print("--- %s seconds ---" % ((time.time() - started_time)))
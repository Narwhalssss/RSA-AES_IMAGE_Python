from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from PIL import Image
import io
import time
from memory_profiler import memory_usage
from pathlib import Path

# Load image and convert to byte array
def image_to_byte_array(image: Image) -> bytes:
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

# Generate RSA Keys
def generate_rsa_keys():
    key = rsa.generate_private_key(
        backend=default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    return key, key.public_key()

# Encryption and Decryption Functions
def rsa_encrypt(public_key, data):
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def rsa_decrypt(private_key, encrypted_data):
    return private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# Measure time and memory usage
def measure_time_and_memory(func, *args):
    start_time = time.time()
    mem_usage = memory_usage((func, args), interval=0.01)
    end_time = time.time()

    time_taken = end_time - start_time
    max_memory = max(mem_usage) - min(mem_usage)
    
    return time_taken, max_memory

def main():
    print("Initializing RSA encryption and decryption...")
    private_key, public_key = generate_rsa_keys()

    # Define a list of image file paths
    image_files = ['C:/Users/robyr/OneDrive/Desktop/test/test3.webp']  # Add your file paths here

    for image_path in image_files:
        print(f"Processing {image_path}...")

        # Load Image
        print("Loading the image...")
        image = Image.open(image_path)
        byte_data = image_to_byte_array(image)

        # Chunk Size (depends on RSA key size)
        chunk_size = 190  # For 2048-bit keys, adjust as necessary
        num_chunks = len(byte_data) // chunk_size + (1 if len(byte_data) % chunk_size else 0)

        # Encrypt Image in Chunks
        print("Starting the encryption process...")
        total_encryption_time = 0
        total_encryption_memory = 0
        encrypted_chunks = []
        for i in range(0, len(byte_data), chunk_size):
            print(f"Encrypting chunk {i // chunk_size + 1}/{num_chunks}")
            chunk = byte_data[i:i + chunk_size]
            time_taken, memory_used = measure_time_and_memory(rsa_encrypt, public_key, chunk)
            encrypted_chunk = rsa_encrypt(public_key, chunk)
            encrypted_chunks.append(encrypted_chunk)
            total_encryption_time += time_taken
            total_encryption_memory += memory_used

        print(f"Encryption completed. Total Time: {total_encryption_time} s, Total Memory: {total_encryption_memory} MiB")

        # Decrypt Image
        print("Starting the decryption process...")
        total_decryption_time = 0
        total_decryption_memory = 0
        decrypted_data = b''
        for i, chunk in enumerate(encrypted_chunks):
            print(f"Decrypting chunk {i + 1}/{num_chunks}")
            time_taken, memory_used = measure_time_and_memory(rsa_decrypt, private_key, chunk)
            decrypted_chunk = rsa_decrypt(private_key, chunk)
            decrypted_data += decrypted_chunk
            total_decryption_time += time_taken
            total_decryption_memory += memory_used

        print(f"Decryption completed. Total Time: {total_decryption_time} s, Total Memory: {total_decryption_memory} MiB")

        # Save the decrypted image
        file_path = Path(image_path)
        decrypted_image_name = f'decrypted_{file_path.stem}{file_path.suffix}'
        print(f"Saving the decrypted image as '{decrypted_image_name}'...")
        decrypted_image = Image.open(io.BytesIO(decrypted_data))

        # Convert to 'RGB' if the image is 'RGBA' and the format doesn't support alpha channel
        if decrypted_image.mode == 'RGBA' and file_path.suffix not in ['.png', '.webp']:
            decrypted_image = decrypted_image.convert('RGB')

        decrypted_image.save(decrypted_image_name)
        print(f"Decrypted image saved as '{decrypted_image_name}'")

    print("Script execution for all images completed.")

if __name__ == '__main__':
    main()
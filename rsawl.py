from PIL import Image
import io
import random
import time
from memory_profiler import memory_usage
from pathlib import Path

# Basic RSA Implementation
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def generate_prime_number():
    while True:
        prime_candidate = random.randint(2**10, 2**11)  # Larger prime numbers
        if is_prime(prime_candidate):
            return prime_candidate

def compute_n(p, q):
    return p * q

def compute_phi(p, q):
    return (p - 1) * (q - 1)

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def choose_e(phi):
    e = random.randint(2, phi - 1)
    while gcd(e, phi) != 1:
        e = random.randint(2, phi - 1)
    return e

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    return x1 + m0 if x1 < 0 else x1

def rsa_encrypt(e, n, data):
    return [pow(byte, e, n) for byte in data]

def rsa_decrypt(d, n, data):
    return bytes([pow(value, d, n) for value in data])

# Image to Byte Array
def image_to_byte_array(image: Image) -> bytes:
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image.format)
    imgByteArr = imgByteArr.getvalue()
    return imgByteArr

# Measure time and memory usage
def measure_time_and_memory(func, *args):
    start_time = time.time()
    mem_usage = memory_usage((func, args), interval=0.01)
    end_time = time.time()

    time_taken = end_time - start_time
    max_memory = max(mem_usage) - min(mem_usage)
    
    return time_taken, max_memory

# Process in Chunks with Time and Memory Measurement
def process_in_chunks_with_measurement(process_func, data, chunk_size):
    total_time = 0
    total_memory = 0
    results = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        time_taken, memory_used = measure_time_and_memory(process_func, chunk)
        processed_chunk = process_func(chunk)
        results.append(processed_chunk)
        total_time += time_taken
        total_memory += memory_used
        print(f"Chunk {i // chunk_size + 1}: Time = {time_taken} seconds, Memory = {memory_used} MiB")
    return results, total_time, total_memory

# Main Function
def main():
    print("Generating RSA keys...")
    p = generate_prime_number()
    q = generate_prime_number()
    n = compute_n(p, q)
    phi = compute_phi(p, q)
    e = choose_e(phi)
    d = modinv(e, phi)

    # Define a list of image file paths
    image_files = ['C:/Users/robyr/OneDrive/Desktop/rsa_test/test3.webp']  # Add your file paths here

    for image_path in image_files:
        print(f"Processing {image_path}...")

        # Load Image
        print("Loading the image...")
        image = Image.open(image_path)
        byte_data = image_to_byte_array(image)

        chunk_size = 190  # Adjusted chunk size for larger key size

        print("Starting the encryption process...")
        encrypted_chunks, total_encryption_time, total_encryption_memory = process_in_chunks_with_measurement(
            lambda chunk: rsa_encrypt(e, n, chunk), byte_data, chunk_size)

        # Flatten the list of lists into a single list of integers
        flat_encrypted_data = [val for sublist in encrypted_chunks for val in sublist]

        print("Starting the decryption process...")
        decrypted_chunks, total_decryption_time, total_decryption_memory = process_in_chunks_with_measurement(
            lambda chunk: rsa_decrypt(d, n, chunk), flat_encrypted_data, chunk_size)
        decrypted_data = b''.join(decrypted_chunks)

        # Convert decrypted data back to image
        file_path = Path(image_path)
        output_dir = file_path.parent
        decrypted_image_name = output_dir / f'decrypted_{file_path.stem}{file_path.suffix}'
        print(f"Saving the decrypted image as '{decrypted_image_name}'...")
        decrypted_image = Image.open(io.BytesIO(decrypted_data))

        # Convert to 'RGB' if the image is 'RGBA' and the format doesn't support alpha channel
        if decrypted_image.mode == 'RGBA' and file_path.suffix not in ['.png', '.webp']:
            decrypted_image = decrypted_image.convert('RGB')

        decrypted_image.save(decrypted_image_name)
        print(f"Decrypted image saved as '{decrypted_image_name}'")

        # Display total times and memory usage for each image
        print(f"Total Encryption Time for {image_path}: {total_encryption_time} seconds")
        print(f"Total Encryption Memory for {image_path}: {total_encryption_memory} MiB")
        print(f"Total Decryption Time for {image_path}: {total_decryption_time} seconds")
        print(f"Total Decryption Memory for {image_path}: {total_decryption_memory} MiB")

    print("Script execution for all images completed.")

if __name__ == '__main__':
    main()

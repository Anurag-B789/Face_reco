import os
import base64
import shutil
import sys


CONFIDENCE_THRESHOLD = 0.6
AUTHORIZED_DIR = "Dataset/Authorized"
ENCODINGS_DIR = "Dataset/face_encodings"
ATTENDANCE_LOG = "attendance_log.json"
CREDENTIALS_FILE = "admin_credentials.enc"
ENCRYPTION_KEY = b'SimpleKey123'
MODELS = "Dataset/models/best2.pt"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def setup_directories():
    if not os.path.exists(ENCODINGS_DIR):
        os.makedirs(ENCODINGS_DIR, exist_ok=True)
    if not os.path.exists(AUTHORIZED_DIR):
        os.makedirs(AUTHORIZED_DIR, exist_ok=True)
    if not os.path.exists(MODELS):
        os.makedirs(os.path.dirname(MODELS), exist_ok=True)
        model_path = resource_path("Dataset/models/best2.pt")
        if os.path.exists(model_path):
            shutil.copy(model_path, MODELS)
        else:
            print(f"Error: Model file {model_path} is missing!")


def encrypt(data):
    data_bytes = data.encode()
    encrypted_bytes = bytes([b ^ k for b, k in zip(data_bytes, ENCRYPTION_KEY * (len(data_bytes) // len(ENCRYPTION_KEY) + 1))])
    return base64.b64encode(encrypted_bytes).decode()

def decrypt(data):
    encrypted_bytes = base64.b64decode(data.encode())
    decrypted_bytes = bytes([b ^ k for b, k in zip(encrypted_bytes, ENCRYPTION_KEY * (len(encrypted_bytes) // len(ENCRYPTION_KEY) + 1))])
    return decrypted_bytes.decode()
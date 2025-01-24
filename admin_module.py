import os
import cv2
import json
import face_recognition
import numpy as np
import shutil
from tkinter import Tk, filedialog
from utils import (
    AUTHORIZED_DIR, ENCODINGS_DIR, ATTENDANCE_LOG,
    CREDENTIALS_FILE, ENCRYPTION_KEY, encrypt, decrypt
)


class AdminManager:
    def __init__(self):
        self.create_default_credentials()
        Tk().withdraw()

    def create_default_credentials(self):
        if not os.path.exists(CREDENTIALS_FILE):
            credentials = {"admin": "Anurag123"}
            encrypted_data = encrypt(json.dumps(credentials))
            with open(CREDENTIALS_FILE, "w") as f:
                f.write(encrypted_data)

    def login(self, username, password):
        try:
            with open(CREDENTIALS_FILE, "r") as f:
                stored_credentials = json.loads(decrypt(f.read()))
                return username in stored_credentials and stored_credentials[username] == password
        except:
            return False

    def select_employee_photo(self):
        file_path = filedialog.askopenfilename(
            title="Select Employee Photo",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*")
            ]
        )

        return file_path if file_path else None

    def add_employee(self, name, face_system):
        print("\nPlease select the employee's photo...")
        photo_path = self.select_employee_photo()

        if not photo_path:
            print("No photo selected. Employee not added.")
            return

        try:
            img = cv2.imread(photo_path)
            if img is None:
                print("Error: Could not read the image file.")
                return

            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_img)

            if not face_locations:
                print("Error: No face detected in the photo. Please use a clear photo with a face.")
                return

            if len(face_locations) > 1:
                print("Error: Multiple faces detected in the photo. Please use a photo with only one face.")
                return

            face_encodings = face_recognition.face_encodings(rgb_img, face_locations)
            if not face_encodings:
                print("Error: Could not generate face encoding. Please use a clearer photo.")
                return

            encoding = face_encodings[0]

            os.makedirs(AUTHORIZED_DIR, exist_ok=True)
            os.makedirs(ENCODINGS_DIR, exist_ok=True)

            # file_extension = os.path.splitext(photo_path)[1]
            # new_photo_path = os.path.join(AUTHORIZED_DIR, f"{name}{file_extension}")
            # shutil.copy2(photo_path, new_photo_path)

            with open(os.path.join(ENCODINGS_DIR, f"{name}.json"), "w") as f:
                json.dump({
                    "name": name,
                    "encoding": encoding.tolist(),
                    # "photo_path": new_photo_path
                }, f)

            face_system.reload_encodings()
            print(f"Employee {name} added successfully!")

        except Exception as e:
            print(f"Error adding employee: {e}")
            # if 'new_photo_path' in locals() and os.path.exists(new_photo_path):
            #     os.remove(new_photo_path)

    def update_employee(self, name, face_system):
        if not os.path.exists(os.path.join(ENCODINGS_DIR, f"{name}.json")):
            print(f"Employee {name} not found!")
            return

        print("\n1. Update Name")
        # print("2. Update Photo")
        # print("3. Update Both")
        choice = input("Enter choice (1): ")

        try:
            with open(os.path.join(ENCODINGS_DIR, f"{name}.json"), "r") as f:
                current_data = json.load(f)

            new_name = name
            # new_photo_path = current_data.get('photo_path')

            if choice in ['1']:
                new_name = input("Enter new name: ")

            # if choice in ['2', '3']:
            #     print("\nPlease select the new photo...")
            #     photo_path = self.select_employee_photo()
            #     if photo_path:
            #         file_extension = os.path.splitext(photo_path)[1]
            #         new_photo_path = os.path.join(AUTHORIZED_DIR, f"{new_name}{file_extension}")
            #         shutil.copy2(photo_path, new_photo_path)
            #
            #         if 'photo_path' in current_data and os.path.exists(current_data['photo_path']):
            #             os.remove(current_data['photo_path'])
            #     else:
            #         print("No new photo selected. Keeping existing photo.")
            #
            # if choice in ['2', '3'] and photo_path:
            #     encoding = np.random.rand(128)
            # else:
            #     encoding = current_data['encoding']

            if new_name != name:
                old_encoding_path = os.path.join(ENCODINGS_DIR, f"{name}.json")
                if os.path.exists(old_encoding_path):
                    os.remove(old_encoding_path)

            with open(os.path.join(ENCODINGS_DIR, f"{new_name}.json"), "w") as f:
                json.dump({
                    "name": new_name,
                    # "encoding": encoding,
                    # "photo_path": new_photo_path
                }, f)

            face_system.reload_encodings()
            print("Employee updated successfully!")

        except Exception as e:
            print(f"Error updating employee: {e}")

    def delete_employee(self, name, face_system):
        try:
            encoding_path = os.path.join(ENCODINGS_DIR, f"{name}.json")
            if os.path.exists(encoding_path):
                with open(encoding_path, "r") as f:
                    employee_data = json.load(f)

                if 'photo_path' in employee_data and os.path.exists(employee_data['photo_path']):
                    os.remove(employee_data['photo_path'])

                os.remove(encoding_path)

                face_system.reload_encodings()
                print(f"Employee {name} deleted successfully!")
            else:
                print(f"Employee {name} not found!")

        except Exception as e:
            print(f"Error deleting employee: {e}")

    def view_employees(self):
        if not os.path.exists(ENCODINGS_DIR):
            print("No employees enrolled yet!")
            return

        print("\nEnrolled Employees:")
        try:
            for file in os.listdir(ENCODINGS_DIR):
                if file.endswith(".json"):
                    with open(os.path.join(ENCODINGS_DIR, file), "r") as f:
                        data = json.load(f)
                        print(f"- {data['name']}")
                        # if 'photo_path' in data:
                        #     print(f"  Photo: {data['photo_path']}")
        except Exception as e:
            print(f"Error viewing employees: {e}")

    def view_attendance(self):
        if not os.path.exists(ATTENDANCE_LOG):
            print("No attendance records found!")
            return

        try:
            with open(ATTENDANCE_LOG, "r") as f:
                attendance = json.load(f)

            print("\nAttendance Records:")
            for date, employees in attendance.items():
                print(f"\n{date}:")
                for emp in employees:
                    print(f"- {emp}")
        except Exception as e:
            print(f"Error viewing attendance: {e}")
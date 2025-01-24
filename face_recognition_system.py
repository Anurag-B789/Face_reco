import cv2
import face_recognition
import numpy as np
from ultralytics import YOLO
from datetime import datetime
from utils import resource_path

import json
import os
import time
from sklearn.neighbors import KDTree
from utils import ENCODINGS_DIR, ATTENDANCE_LOG

class FaceRecognitionSystem:
    def __init__(self):
        print("Initializing Face Recognition System...")

        print("Loading anti-spoofing model...")
        self.anti_spoof_model = YOLO(resource_path("Dataset/models/best2.pt"))
        model_path = resource_path("Dataset/models/best2.pt")
        print(f"Loading YOLO model from: {model_path}")
        self.anti_spoof_model = YOLO(model_path)
        self.anti_spoof_model.to('cpu')

        self.encodings = []
        self.names = []
        self.kdtree = None
        self.last_spoof_check = 0
        self.spoof_check_interval = 2.0
        self.last_recognition_time = 0
        self.recognition_interval = 2.0
        self.last_result = "No faces detected"
        self.reload_encodings()
        print("System initialized successfully!")

    def reload_encodings(self):
        self.encodings = []
        self.names = []
        if os.path.exists(ENCODINGS_DIR):
            try:
                for file in os.listdir(ENCODINGS_DIR):
                    if file.endswith(".json"):
                        with open(os.path.join(ENCODINGS_DIR, file), "r") as f:
                            data = json.load(f)
                            self.names.append(data["name"])
                            self.encodings.append(np.array(data["encoding"]))
            except Exception as e:
                print(e)
        if len(self.encodings) > 0:
            self.encodings = np.array(self.encodings)
            self.kdtree = KDTree(self.encodings)
        else: print("No encodings")

    def check_spoofing(self, frame):

        current_time = time.time()
        if current_time - self.last_spoof_check < self.spoof_check_interval:
            return True

        self.last_spoof_check = current_time

        try:
            small_frame = cv2.resize(frame, (240, 180))
            results = self.anti_spoof_model(small_frame, verbose=False)

            for r in results:
                if len(r.boxes) > 0:
                    class_id = int(r.boxes[0].cls[0].item())
                    return class_id == 1
            return False
        except Exception as e:
            print(f"Error in spoof checking: {e}")
            return False

    def process_frame(self, frame):
        current_time = time.time()
        if current_time - self.last_recognition_time < self.recognition_interval:
            return self.last_result

        self.last_recognition_time = current_time

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if not face_encodings:
                self.last_result = None
                return "No faces detected"

            if len(face_encodings) > 1:
                self.last_result = "Multiple faces detected - Access Denied"
                return self.last_result

            if not self.check_spoofing(frame):
                self.last_result = "Spoofing attempt detected!"
                cv2.destroyAllWindows()
                time.sleep(2)
                return self.last_result
            else:
                face_encoding = face_encodings[0]

                if self.kdtree is not None:
                    distances, indices = self.kdtree.query([face_encoding], k=1)
                    if distances[0][0] < 0.5:
                        name = self.names[indices[0][0]]
                        self.log_attendance(name)
                        self.last_result = f"Authorized person {name} - Door opened"
                        print(self.last_result)
                        return self.last_result
                    else:
                        self.last_result = "Unauthorized entry detected"
                        return self.last_result

        except Exception as e:
            print(f"Error processing frame: {e}")
            self.last_result = None
            return None

    def log_attendance(self, name):
        try:
            today = datetime.now().strftime("%d-%m-%Y %H:%M")
            attendance = {}

            if os.path.exists(ATTENDANCE_LOG):
                with open(ATTENDANCE_LOG, "r") as f:
                    attendance = json.load(f)

            if today not in attendance:
                attendance[today] = []

            if name not in attendance[today]:
                attendance[today].append(name)
                with open(ATTENDANCE_LOG, "w") as f:
                    json.dump(attendance, f, indent=4)
        except Exception as e:
            print(f"Error logging attendance: {e}")
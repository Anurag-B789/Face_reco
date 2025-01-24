import cv2
from admin_module import AdminManager
from face_recognition_system import FaceRecognitionSystem
from utils import setup_directories
import time


def test_camera():
    print("\nTesting available cameras...")
    for index in range(2):
        print(f"\nTrying camera index {index}...")
        cap = cv2.VideoCapture(index)

        if not cap.isOpened():
            print(f"Could not open camera {index}")
            continue

        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)

        print(f"Camera {index} opened successfully!")
        print(f"Resolution: {width}x{height}")
        # print(f"FPS: {fps}")

        ret, frame = cap.read()
        if ret:
            print(f"Successfully read frame from camera {index}")
            cap.release()
            return index
        else:
            print(f"Could not read frame from camera {index}")

        cap.release()

    return None


def main():
    try:
        setup_directories()
        print("Directories setup correctly")

        face_system = FaceRecognitionSystem()
        print("Face system initialized")

        admin = AdminManager()
        working_camera = test_camera()
        if working_camera is None:
            print("No working camera found! Please check your camera connection and permissions.")
            return

        print(f"\nUsing camera index {working_camera}")

    except Exception as e:
        print(f"Critical error: {e}")
        input("Press Enter to exit...")
    def admin_menu():
        while True:
            print("\nAdmin Menu:")
            print("1. Add Employee")
            print("2. Update Employee")
            print("3. Delete Employee")
            print("4. View Employees")
            print("5. View Attendance")
            print("6. Exit to Main System")

            choice = input("\nEnter your choice (1-6): ")

            if choice == '1':
                name = input("Enter employee name: ")
                admin.add_employee(name, face_system)
            elif choice == '2':
                name = input("Enter employee name to update: ")
                admin.update_employee(name, face_system)
            elif choice == '3':
                name = input("Enter employee name to delete: ")
                admin.delete_employee(name, face_system)
            elif choice == '4':
                admin.view_employees()
            elif choice == '5':
                admin.view_attendance()
            elif choice == '6':
                break
            else:
                print("Invalid choice!")

    print("\nStarting Face Recognition System...")
    print("Press 'a' in the camera window to access admin menu")
    print("Press 'q' to quit")

    while True:
        working_camera = test_camera()

        try:
            cap = cv2.VideoCapture(working_camera, cv2.CAP_DSHOW)

            if not cap.isOpened():
                print("Error: Could not open camera")
                time.sleep(1)
                continue

            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 15)

            time.sleep(3)

            print("\nCamera initialized successfully!")
            # frame_count = 0
            # start_time = time.time()

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # frame_count += 1
                # if frame_count % 30 == 0:
                #     elapsed_time = time.time() - start_time
                #     fps = frame_count / elapsed_time
                #      print(f"FPS: {fps:.2f}")

                result = face_system.process_frame(frame)
                if result:
                    cv2.putText(frame, result, (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                cv2.imshow("Face Recognition System", frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nQuitting...")
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                elif key == ord('a'):
                    cap.release()
                    cv2.destroyAllWindows()

                    username = input("Username: ")
                    password = input("Password: ")

                    if admin.login(username, password):
                        admin_menu()
                    else:
                        print("Invalid credentials!")

                    print("\nRestarting camera...")
                    break

                time.sleep(0.01)
 
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(1)
        finally:
            if 'cap' in locals() and cap.isOpened():
                cap.release()
            cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
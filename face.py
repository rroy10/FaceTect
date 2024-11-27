import cv2
import mediapipe as mp
import face_recognition
import numpy as np
import tkinter as tk
from tkinter import messagebox
from code_2 import AttendanceApp  # Import the AttendanceApp class

# Set up Mediapipe face detection and drawing utilities
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# Load the reference image and obtain face encodings for comparison
reference_image_path = "IMG_9289.jpg"  # Path to the reference image
reference_image = face_recognition.load_image_file(reference_image_path)  # Load the image file
reference_encodings = face_recognition.face_encodings(reference_image)  # Get face encodings

# Check if at least one face encoding is found in the reference image
if len(reference_encodings) == 0:
    raise ValueError("No faces found in the reference image.")  # Raise an error if no faces are found

reference_encoding = reference_encodings[0]  # Use the first face found in the reference image

# Function to validate username and password
def validate_password():
    username = username_entry.get()
    password = password_entry.get()
    if username == "user" and password == "password":
        messagebox.showinfo("Password Verified", "Password is correct. Please proceed with face recognition.")
        recognize_face()  # Proceed to face recognition
    else:
        messagebox.showerror("Login Failed", "Incorrect username or password.")

# Function to perform face recognition
def recognize_face():
    cap = cv2.VideoCapture(0)  # Set up video capture from the default camera
    with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
        while cap.isOpened():
            success, image = cap.read()  # Capture frame from webcam
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_detection.process(image)

            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(image, detection)

                    bboxC = detection.location_data.relative_bounding_box
                    h, w, _ = image.shape
                    x, y, width, height = (int(bboxC.xmin * w), int(bboxC.ymin * h), 
                                           int(bboxC.width * w), int(bboxC.height * h))

                    face_image = image[y:y + height, x:x + width]
                    face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

                    face_encodings = face_recognition.face_encodings(face_image_rgb)

                    if face_encodings:
                        face_encoding = face_encodings[0]
                        results = face_recognition.compare_faces([reference_encoding], face_encoding)

                        if results[0]:  # If a match is found
                            messagebox.showinfo("MFA Success", "Face recognized successfully!")
                            cap.release()
                            cv2.destroyAllWindows()

                            # Launch the Attendance App
                            root.destroy()  # Close the login window
                            new_root = tk.Tk()  # Create a new root for the AttendanceApp
                            AttendanceApp(new_root)  # Instantiate AttendanceApp
                            new_root.mainloop()  # Start the new main loop
                            return
                        else:
                            messagebox.showerror("Login Failed", "Face not recognized.")
                            cap.release()
                            cv2.destroyAllWindows()
                            return

            cv2.imshow('Face Recognition', cv2.flip(image, 1))
            if cv2.waitKey(5) & 0xFF == 27:  # Exit loop if 'Esc' is pressed
                break

    cap.release()
    cv2.destroyAllWindows()

# GUI for the login page
root = tk.Tk()
root.title("FaceTect Login")
root.geometry("300x400")
root.configure(bg="#f9f8f3")

# GUI Style configuration
title_font = ("Helvetica", 24, "bold")
button_font = ("Helvetica", 12, "bold")

# Canvas for logo placeholder
canvas = tk.Canvas(root, width=100, height=100, bg="#f9f8f3", highlightthickness=2, highlightbackground="black")
canvas.create_rectangle(5, 5, 95, 95)  # Draw a square as a placeholder for the logo
canvas.pack(pady=(20, 10))

# Title Label
title_label = tk.Label(root, text="FaceTect", font=title_font, fg="#274584", bg="#f9f8f3")
title_label.pack(pady=(10, 20))

# Username and Password Fields
username_entry = tk.Entry(root, width=25, font=("Helvetica", 12), justify="center")
username_entry.insert(0, "Username")
username_entry.configure(bg="#a6b8e4", fg="white")
username_entry.pack(pady=5, ipady=5)

password_entry = tk.Entry(root, width=25, font=("Helvetica", 12), show="*", justify="center")
password_entry.insert(0, "Password")
password_entry.configure(bg="#a6b8e4", fg="white")
password_entry.pack(pady=5, ipady=5)

# Standard Login Button
login_button = tk.Button(root, text="LOGIN", width=15, font=button_font, bg="#e0e0e0", fg="#274584", command=validate_password)
login_button.pack(pady=(20, 0), ipady=5)

# Run the application
root.mainloop()

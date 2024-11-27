import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import PhotoImage, Scrollbar, Frame, Canvas
from PIL import Image, ImageTk
import cv2
import face_recognition
import numpy as np
import mediapipe as mp

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance App")

        self.students = []  # Store student records
        self.selected_image_path = None
        self.selected_schedule_path = None

        # Initialize MediaPipe face detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils

        # Create main layout
        self.layout = tk.Frame(root, bg="#A3B8F2")
        self.layout.pack(fill=tk.BOTH, expand=True)

        self.create_student_form()
        self.create_students_grid()

    def create_student_form(self):
        self.student_form = tk.Frame(self.layout, bg="#A3B8F2")
        self.student_form.pack(pady=10)

        tk.Label(self.student_form, text="Student Information", font=("Arial", 14, "bold"), bg="#A3B8F2").pack()

        self.first_name_input = tk.Entry(self.student_form, width=30)
        self.first_name_input.insert(0, "First Name *")
        self.first_name_input.pack(pady=5)

        self.last_name_input = tk.Entry(self.student_form, width=30)
        self.last_name_input.insert(0, "Last Name *")
        self.last_name_input.pack(pady=5)

        tk.Button(self.student_form, text="Upload Student Picture", command=self.upload_picture).pack(pady=5)
        tk.Button(self.student_form, text="Save Changes", command=self.add_student).pack(pady=10)
        tk.Button(self.student_form, text="Start Face Recognition", command=self.start_face_recognition).pack(pady=5)

    def create_students_grid(self):
        self.students_view = tk.Frame(self.layout)
        self.students_view.pack(pady=10)

        header = tk.Frame(self.students_view)
        header.pack()

        tk.Label(header, text="All Students", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        

        # Search bar
        self.search_entry = tk.Entry(header, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.bind("<KeyRelease>", self.filter_students)

        

        # Create horizontal scrollbar
        self.canvas = Canvas(self.students_view)
        self.horizontal_scrollbar = Scrollbar(self.students_view, orient="horizontal", command=self.canvas.xview)
        self.vertical_scrollbar = Scrollbar(self.students_view, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vertical_scrollbar.set)
        self.canvas.configure(xscrollcommand=self.horizontal_scrollbar.set)

        self.horizontal_scrollbar.pack(side="bottom", fill="x")
        self.vertical_scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

    def upload_picture(self):
        self.selected_image_path = filedialog.askopenfilename(
            title="Select a picture",
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if self.selected_image_path:
            print(f"Selected image: {self.selected_image_path}")

    def add_student(self):
        first_name = self.first_name_input.get().strip()
        last_name = self.last_name_input.get().strip()

        if first_name and last_name and self.selected_image_path:
            full_name = f"{first_name} {last_name}"
            student_id = len(self.students) + 1

            # Load and encode the student's picture
            student_image = face_recognition.load_image_file(self.selected_image_path)
            student_encoding = face_recognition.face_encodings(student_image)[0]

            self.students.append({
                'id': student_id,
                'name': full_name,
                'photo_path': self.selected_image_path,
                'encoding': student_encoding,
                'status': None
            })

            self.add_student_to_grid(self.students[-1])
            self.first_name_input.delete(0, tk.END)
            self.last_name_input.delete(0, tk.END)
            self.selected_image_path = None

    def add_student_to_grid(self, student):
        student_frame = tk.Frame(self.scrollable_frame, bd=2, relief=tk.GROOVE)
        student_frame.pack(pady=5, fill="x")

        img = Image.open(student['photo_path'])
        img = img.resize((100, 100), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        img_label = tk.Label(student_frame, image=photo)
        img_label.image = photo
        img_label.pack(side=tk.LEFT)

        tk.Label(student_frame, text=student['name'], font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        student['frame'] = student_frame  # Store the frame reference

        # Present/Absent Toggle Switch
        self.status_var = tk.BooleanVar(value=False)  # Default to Absent
        toggle = tk.Checkbutton(student_frame, text="Present", variable=self.status_var,
                                 command=lambda s=student: self.toggle_present_absent(s))
        toggle.pack(side=tk.LEFT)

        # Delete button
        tk.Button(student_frame, text="Delete", command=lambda s=student: self.delete_student(s)).pack(side=tk.LEFT)

    def filter_students(self, event):
        search_term = self.search_entry.get().lower()
        for student in self.students:
            student_name = student['name'].lower()
            if search_term in student_name:
                student['frame'].pack(pady=5, fill="x")
            else:
                student['frame'].pack_forget()

    def toggle_present_absent(self, student):
        if self.status_var.get():
            self.mark_present(student)
        else:
            self.mark_absent(student)

    def mark_present(self, student):
        student['frame'].config(bg='lightgreen')
        student['status'] = 'Present'

    def mark_absent(self, student):
        student['frame'].config(bg='red')
        student['status'] = 'Absent'

    def delete_student(self, student):
        student['frame'].pack_forget()
        self.students.remove(student)

    def start_face_recognition(self):
        cap = cv2.VideoCapture(0)
        MATCH_THRESHOLD = 0.6  # Adjusted threshold
        unsuccessful_attempts = 0  # Counter for unsuccessful attempts

        with self.mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5) as face_detection:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame.")
                    break

                # Convert the frame to RGB for MediaPipe processing
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_frame)

                if results.detections:
                    for detection in results.detections:
                        # Draw face landmarks
                        self.mp_drawing.draw_detection(frame, detection)

                        # Extract bounding box
                        bboxC = detection.location_data.relative_bounding_box
                        h, w, _ = frame.shape
                        x, y, width, height = (int(bboxC.xmin * w), int(bboxC.ymin * h),
                                            int(bboxC.width * w), int(bboxC.height * h))

                        # Extract face area
                        face_image = frame[y:y + height, x:x + width]
                        face_image_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)

                        # Get face encodings for the detected face
                        face_encodings = face_recognition.face_encodings(face_image_rgb)

                        if face_encodings:  # If a face is found
                            face_encoding = face_encodings[0]

                            # Compare with all student encodings
                            distances = face_recognition.face_distance(
                                [student['encoding'] for student in self.students], face_encoding
                            )
                            matches = distances < MATCH_THRESHOLD

                            if True in matches:
                                match_index = np.argmin(distances)
                                matched_student = self.students[match_index]
                                self.highlight_student(matched_student)
                                print(f"Match found: {matched_student['name']}")
                                # Reset unsuccessful attempts on a match
                                unsuccessful_attempts = 0
                                # Toggle switch to Present
                                matched_student['frame'].children['!checkbutton'].select()  # Check the toggle
                            else:
                                # Increment unsuccessful attempts
                                unsuccessful_attempts += 1
                                if unsuccessful_attempts >= 5:
                                    messagebox.showwarning("Safety Alert", "SAFETY ALERT!!")
                                    unsuccessful_attempts = 0  # Reset counter after alert

                # Display the frame with bounding boxes
                cv2.imshow('Face Recognition', frame)
                if cv2.waitKey(5) & 0xFF == 27:
                    break

        cap.release()
        cv2.destroyAllWindows()

    def highlight_student(self, student):
        student['frame'].config(bg='lightgreen')
        self.mark_present(student)
        self.root.update_idletasks()

# Run the application
if __name__ == '__main__':
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()

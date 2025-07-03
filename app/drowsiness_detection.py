import cv2
import pygame
import dlib
import numpy as np
import requests
from imutils import face_utils
import os

class DrowsinessDetection:
    def __init__(self, status_callback):
        # Initialize camera with a more explicit backend (DirectShow for Windows)
        self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cam.isOpened():
            print("Error: Could not access the camera in DrowsinessDetection.")
            return
        else:
            print("Camera initialized successfully.")

        # Set camera resolution
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Initialize dlib face detector and shape predictor
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        # Parameters for eye aspect ratio (EAR)
        self.EAR_THRESHOLD = 0.3
        self.EAR_FRAMES = 30
        self.COUNTER = 0

        # Callback function to update status
        self.status_callback = status_callback

        # Initialize pygame for sound alert
        pygame.mixer.init()
        # Provide the full path or correct relative path for the alarm sound file
        alarm_path = os.path.join(os.getcwd(), 'red_alert', 'alarm.mp3')
        if os.path.exists(alarm_path):
            pygame.mixer.music.load(alarm_path)
        else:
            print(f"Error loading alarm sound: {alarm_path} not found.")

    def send_to_thingspeak(self, latitude, longitude, status):
        channelID = '549041'
        writeAPIKey = '1Y5AWUR4KI7Y1FMW'
        url = f"https://api.thingspeak.com/update?api_key={writeAPIKey}&field1={latitude}&field2={longitude}&field3={status}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Data sent successfully: {status} at {latitude}, {longitude}")
            else:
                print(f"Error sending data: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

    def update_frame(self):
        ret, frame = self.cam.read()
        if not ret:
            print("Error: Failed to capture frame.")
            return

        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Ensure that the gray image is 8-bit single-channel (grayscale)
        if gray is None or len(gray.shape) != 2:
            print("Error: Invalid grayscale image.")
            return

        faces = self.detector(gray, 0)

        if faces:
            for face in faces:
                shape = self.predictor(gray, face)
                shape = face_utils.shape_to_np(shape)
                leftEye = shape[42:48]
                rightEye = shape[36:42]
                self.highlight_eyes(frame, leftEye, rightEye)

                l_EAR = self.eye_aspect_ratio(leftEye)
                r_EAR = self.eye_aspect_ratio(rightEye)
                EAR = (l_EAR + r_EAR) / 2

                if EAR < self.EAR_THRESHOLD:
                    self.COUNTER += 1
                    if self.COUNTER >= self.EAR_FRAMES:
                        pygame.mixer.music.play(-1)
                        status = "ALERT"
                        self.send_to_thingspeak(11.0901801, 77.0184452, status)
                        self.status_callback(status, 11.0901801, 77.0184452)
                else:
                    pygame.mixer.music.stop()
                    self.COUNTER = 0
                    self.status_callback("Normal", None, None)

        cv2.imshow("Drowsiness Detection", frame)
        cv2.waitKey(1)

    def highlight_eyes(self, frame, leftEye, rightEye):
        cv2.polylines(frame, [leftEye], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.polylines(frame, [rightEye], isClosed=True, color=(0, 255, 0), thickness=2)

    def eye_aspect_ratio(self, eye):
        A = np.linalg.norm(eye[1] - eye[5])
        B = np.linalg.norm(eye[2] - eye[4])
        C = np.linalg.norm(eye[0] - eye[3])
        return (A + B) / (2.0 * C)

    def run(self):
        while True:
            self.update_frame()

    def release(self):
        self.cam.release()
        cv2.destroyAllWindows()

# Callback function to update the status
def status_callback(status, latitude, longitude):
    if latitude is not None and longitude is not None:
        print(f"Status: {status} | Latitude: {latitude} | Longitude: {longitude}")
    else:
        print(f"Status: {status}")

if __name__ == "__main__":
    drowsiness_detector = DrowsinessDetection(status_callback)
    if hasattr(drowsiness_detector, 'cam') and drowsiness_detector.cam.isOpened():
        try:
            drowsiness_detector.run()
        except KeyboardInterrupt:
            print("Detection interrupted by user.")
        finally:
            drowsiness_detector.release()

import os
import json
import numpy as np
import cv2
import time
import face_recognition
from PIL import Image
# from ST7789 import ST7789

KNOW_PEOPLE_DIR_PATH_NAME = "known_people"
JSON_FILE_NAME = "faces.json"
PATH_TO_ROOT = os.getcwd()

# Get a reference to webcam #
# (the default one)
# for mac: 1
# for pi: 0
CAM_REF = 1

SPI_SPEED_MHZ = 80

# st7789 = ST7789(
#     rotation=90*2,  # Needed to display the right way up on Pirate Audio
#     port=0,       # SPI port
#     cs=1,         # SPI port Chip-select channel
#     dc=9,         # BCM pin used for data/command
#     backlight=13,
#     spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
# )

def load_encoded_files(path2root=PATH_TO_ROOT):
    # go to directory with people sub-directories & get people names
    people_dir_path = os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME)
    os.chdir(people_dir_path)
    names = list(filter(os.path.isdir, os.listdir(os.curdir)))

    # get path to faces.json
    encoded_faces_json_path = []
    for name in names:
        encoded_faces_json_path.append(
            os.path.join(path2root, KNOW_PEOPLE_DIR_PATH_NAME, name, JSON_FILE_NAME)
        )

    # get file.json to python array
    encoded_faces = {}
    for encoded_face_json in encoded_faces_json_path:
        with open(encoded_face_json) as json_file:
            data = json.load(json_file)
        for name in data:
            encoded_faces[name] = data[name]

    # get python array to np array
    encoded_faces_np = {}
    for name in encoded_faces:
        encoded_faces_np[name] = []
        for encoded_face in encoded_faces[name]:
            encoded_face_np = np.array(encoded_face)
            # encoded_face_np = np.ndarray(encoded_face)
            encoded_faces_np[name].append(encoded_face_np)

    # prepare to return
    known_face = {
        "encodings": [],
        "names": []
    }
    for name in encoded_faces_np:
        for encoded_face_np in encoded_faces_np[name]:
            known_face["names"].append(name)
            known_face["encodings"].append(encoded_face_np)

    return known_face

def start_cam_and_staff(known_face):
    video_capture = cv2.VideoCapture(CAM_REF)

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # start
    while True:
    
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face["encodings"], face_encoding)
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face["encodings"], face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face["names"][best_match_index]

                face_names.append(name)
            print(*face_names)

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            
        # Display the resulting image
        cv2.imshow('Video', frame)

        # mini led
        miniLedImage = np.array(frame)
        miniLedImage = cv2.resize(miniLedImage, (240, 240))
        pil_image=Image.fromarray(miniLedImage)
        # st7789.display(pil_image)
            
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        process_this_frame = not process_this_frame

if __name__ == '__main__':
    known_face = load_encoded_files()
    start_cam_and_staff(known_face)
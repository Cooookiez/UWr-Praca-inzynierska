import os
import face_recognition
import time
from PIL import Image
import warnings
import cv2
import numpy as np
from ST7789 import ST7789

SPI_SPEED_MHZ = 80

st7789 = ST7789(
    rotation=90*2,  # Needed to display the right way up on Pirate Audio
    port=0,       # SPI port
    cs=1,         # SPI port Chip-select channel
    dc=9,         # BCM pin used for data/command
    backlight=13,
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)

path = {
    "personal_path": {}
}
valid_image_exts = [".jpg", ".jpeg", ".png"]
known_people_photos = {} # path to all images of known peaple

known_face_encodings = []
known_face_names = []

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def encode_known_peapel():
    path["known_people"] = os.path.join(path["cwd"], "known_people")

    # load known people & set paths to them
    os.chdir(path["known_people"])
    directories_in_curdir = list(filter(os.path.isdir, os.listdir(os.curdir)))
    known_people_names = directories_in_curdir.copy()
    for person_name in known_people_names:
        path["personal_path"][person_name] = os.path.join(path["known_people"], person_name)

    # set path of all image in peaple folder
    for person in path["personal_path"]:
        person_photos = []
        for file in os.listdir(path["personal_path"][person]):
            ext = os.path.splitext(file)[1] # either valid or unvalid file extension
            if ext.lower() in valid_image_exts:
                person_photos.append(os.path.join(path["personal_path"][person], file))
        known_people_photos[person] = person_photos

    # encode faces
    # Load a sample picture and learn how to recognize it.
    print("Start encoding, pleas wait...")
    time_start = time.time()
    index = 0
    index_max = len(known_people_photos)
    for person in known_people_photos:
        
        index += 1
        print(f"\tLoading \"{person}\" ({index} / {index_max}) ...")

        img_index = 0
        img_index_max = len(known_people_photos[person])
        for img in known_people_photos[person]:
            img_index += 1
            try:
                person_image = face_recognition.load_image_file(img)
                person_face_encoding = face_recognition.face_encodings(person_image)

                if len(person_face_encoding) >= 1:
                    person_face_encoding = person_face_encoding[0]
                    # append
                    known_face_encodings.append(person_face_encoding)
                    known_face_names.append(person)
                else:
                    # warnings.warn("Face encoding too similar to previous one. skipped.")
                    pass

                print(f"\t\t({img_index} / {img_index_max}) Image Loaded")

            except:
                print(f"\t\t({img_index} / {img_index_max}) Image {img} either invalid or has invalid face on it")
                pass
        
        # print(f"\t\tDONE")

    time_end = time.time()
    time_diffrence = time_end - time_start
    print(f"All Done! ({time_diffrence} s)")

if __name__ == '__main__':

    # make paths
    path["cwd"] = os.getcwd()

    # encode known peapel to ...
    encode_known_peapel()

    # Get a reference to webcam #0 (the default one)
    video_capture = cv2.VideoCapture(0)

    print("pres 'q' to exit")

    while True:

        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

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
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
            print(*face_names)

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

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
        st7789.display(pil_image)
            
        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        process_this_frame = not process_this_frame

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
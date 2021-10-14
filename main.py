import os
import face_recognition
import time
from PIL import Image
import warnings
import cv2

path = {
    "personal_path": {}
}
valid_image_exts = [".jpg", ".jpeg", ".png"]
known_people_photos = {} # path to all images of known peaple

known_face_encodings = []
known_face_names = []

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

    # encode known peapel to ... # todo
    encode_known_peapel()

    pass
import os
import json
import numpy as np

KNOW_PEOPLE_DIR_PATH_NAME = "known_people"
JSON_FILE_NAME = "faces.json"
PATH_TO_ROOT = os.getcwd()

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

if __name__ == '__main__':
    # known_face = {
    #     "encodings": [],
    #     "names": []
    # }
    known_face = load_encoded_files()
    print(len(known_face["names"]))
    print(known_face["names"])
    pass
    
import config_helper as ch

# # # # # # # # # # #
#     IMPORTANT     #
# # # # # # # # # # #

CAM_REF = 1 # mac=1, pi=0
CAM_ROTATION = ch.rotate[0] # 0, 90, 180, 270

# # # # # # # # # # #
#  NOT SO IMPORTANT #
# # # # # # # # # # #

valid_image_exts = [".jpg", ".jpeg", ".png"]
KNOW_PEOPLE_DIR_PATH_NAME = "known_people"
JSON_FILE_NAME = "faces.json"
UNKNOWN_NAME = "Unknown"
WELCOMES_DIR_PATH_NAME = "welcomes"
ALERT_DELAY_IGNORE = 5 # seconds
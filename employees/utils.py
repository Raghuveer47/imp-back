from deepface import DeepFace
import cv2
import numpy as np
import base64
from PIL import Image
from geopy.distance import geodesic

def get_face_encoding_from_base64(base64_str):
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]

        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        rgb_image = np.array(image.convert('RGB'))

        face_locations = face_recognition.face_locations(rgb_image)
        encodings = face_recognition.face_encodings(rgb_image, face_locations)

        if encodings:
            return encodings[0]  # ✅ return a single numpy array
        return None
    except Exception as e:
        print("❌ Error in get_face_encoding_from_base64:", e)
        return None

def is_within_location(user_lat, user_lon, office_lat, office_lon):
    user_location = (user_lat, user_lon)
    office_location = (office_lat, office_lon)
    return geodesic(user_location, office_location).meters  # returns distance in meters
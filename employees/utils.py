import numpy as np
import base64
import io
from PIL import Image
from geopy.distance import geodesic
from sklearn.metrics.pairwise import cosine_similarity

def get_face_encoding_from_base64(base64_str):
    """
    Extract face encoding from base64 image using face-api.js descriptors
    This function will be called by the frontend which sends the descriptor directly
    """
    try:
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]

        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        rgb_image = np.array(image.convert('RGB'))

        # For now, return a dummy encoding since the frontend will send the descriptor
        # TODO: Implement face detection and encoding extraction if needed
        dummy_encoding = np.zeros(128, dtype=np.float64)
        return dummy_encoding
    except Exception as e:
        print("❌ Error in get_face_encoding_from_base64:", e)
        return None

def compare_face_descriptors(descriptor1, descriptor2, threshold=0.6):
    """
    Compare two face descriptors using cosine similarity
    descriptor1, descriptor2: numpy arrays of shape (128,)
    threshold: similarity threshold (lower = more strict)
    """
    try:
        # Reshape descriptors for cosine_similarity
        desc1 = descriptor1.reshape(1, -1)
        desc2 = descriptor2.reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(desc1, desc2)[0][0]
        
        # Convert similarity to distance (1 - similarity)
        distance = 1 - similarity
        
        # Return True if distance is below threshold (similar faces)
        return distance < threshold, distance
    except Exception as e:
        print("❌ Error in compare_face_descriptors:", e)
        return False, 1.0

def is_within_location(user_lat, user_lon, office_lat, office_lon):
    user_location = (user_lat, user_lon)
    office_location = (office_lat, office_lon)
    return geodesic(user_location, office_location).meters  # returns distance in meters
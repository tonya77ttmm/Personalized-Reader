import cv2
from pathlib import Path

from mediapipe.tasks import python

from mediapipe.tasks.python import vision
import numpy as np
import mediapipe as mp
from .FaceExtractor import FaceExtractor


class MediaPipeExtractor(FaceExtractor):

    def __init__(self):
        #Model 0 Optimized for nearby faces.
        #So only predictions above 50% are returned. the model confidence is above 50
        PROJECT_ROOT = Path(__file__).resolve().parents[3]

        model_path = (

            PROJECT_ROOT

            / "app"

            / "models"

            / "detector.tflite"

        )

        base_options = python.BaseOptions(

            model_asset_path=str(model_path)

        )

        options = vision.FaceDetectorOptions(

            base_options=base_options,

            min_detection_confidence=0.5

        )

        self.detector = vision.FaceDetector.create_from_options(

            options

        )

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        # Guard against empty/None frames
        if image is None or image.size == 0:
            print("MediaPipeExtractor warning: Received empty frame. Skipping.")
            return None, None
        #image is loaded as a BGR image from OpenCV and it's np.ndarray
        #mediapipe requires RGB image for processing, so we need to convert it to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(

    image_format=mp.ImageFormat.SRGB,

    data=rgb

)

        print("start detecting", flush=True)

        results = self.detector.detect(mp_image)

        print("finish detecting", flush=True)

        if not results.detections:

            raise ValueError("No face detected")

        detection = results.detections[0]

        bbox = detection.bounding_box

        x = bbox.origin_x

        y = bbox.origin_y

        bw = bbox.width

        bh = bbox.height

        face = image[y:y+bh, x:x+bw]

        face_box = {

    "x": x,

    "y": y,

    "width": bw,

    "height": bh,

}

        return face, face_box
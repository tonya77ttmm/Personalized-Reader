from abc import ABC, abstractmethod
import numpy as np

class FaceExtractor(ABC):

    @abstractmethod
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Input:
            image - BGR image from OpenCV

        Returns:
            aligned/cropped face as a numpy array

        Raises:
            ValueError if no face is detected.
        """
        pass
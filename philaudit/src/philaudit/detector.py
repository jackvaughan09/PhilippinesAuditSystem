import numpy as np
import torch

from .model import PhilTableDetection
from .transforms import DEFAULT_TRANSFORMS


class Detector:
    """
    A wrapper for the PhilTableDetection model that handles loading the model,
    transforming the input image, and returning the prediction.
    Example:
    ```
    from philaudit.detect.detector import Detector
    model_weights = "path/to/model/weights.ckpt"
    my_detector = Detector(model_weights)
    prediction = my_detector.detect(image)
    ```
    """

    def __init__(self, model_weights):
        self.map_location = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        self.model = self._load_model(model_weights)
        self.transforms = DEFAULT_TRANSFORMS

    def detect(self, image):
        image = self._transform(image)
        prediction = self._predict(image)
        return prediction

    def _transform(self, image):
        image = np.asarray(image)
        return self.transforms(image=image)["image"]

    def _predict(self, image):
        image = image.unsqueeze(0)  # Add an extra dimension for the batch size
        logit = self.model(image)
        prediction = torch.sigmoid(logit)
        return 1 if prediction[0][0] > 0.5 else 0

    def _load_model(self, model_weights):
        model = PhilTableDetection.load_from_checkpoint(
            model_weights, map_location=self.map_location
        )
        model.eval()
        model.requires_grad_(False)
        return model

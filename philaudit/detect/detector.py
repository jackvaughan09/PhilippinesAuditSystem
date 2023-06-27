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
        self.model = self._load_model(model_weights)
        self.transforms = DEFAULT_TRANSFORMS
        self.map_location = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )

    def detect(self, image):
        image = self._transform(image, self.transforms)
        prediction = self._predict(self.model, image)
        return prediction

    def _transform(self, image):
        return self.transforms(np.asarray(image))["image"].unsqueeze(0)

    def _predict(self, image):
        return self.model(image)

    def _load_model(self, model_weights):
        model = PhilTableDetection.load_from_checkpoint(
            model_weights, map_location=self.map_location
        )
        model.eval()
        model.requires_grad_(False)
        return model

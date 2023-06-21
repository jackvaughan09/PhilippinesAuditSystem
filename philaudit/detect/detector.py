import numpy as np
from model import PhilTableDetection
from transforms import DEFAULT_TRANSFORMS


class Detector:
    def __init__(self, model_weights):
        self.model = self._load_model(model_weights)
        self.transforms = DEFAULT_TRANSFORMS

    def detect(self, image):
        image = self._transform(image, self.transforms)
        prediction = self._predict(self.model, image)
        return prediction

    def _transform(self, image):
        return self.transforms(np.asarray(image))["image"].unsqueeze(0)

    def _predict(self, image):
        return self.model(image)

    def _load_model(self, model_weights):
        model = PhilTableDetection.load_from_checkpoint(model_weights)
        model.eval()
        model.requires_grad_(False)
        return model

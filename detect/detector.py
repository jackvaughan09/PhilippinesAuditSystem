from pdf2image import convert_from_path
import numpy as np
from PIL import Image

import albumentations as album
from albumentations.pytorch.transforms import ToTensorV2

from detect.model import PhilTableDetection
from detect.phildata import EnsureLandscape

MODEL_PATH = "./checkpoints"


class Detector:
    def __init__(self, model_path):
        self.model = self._load_model(model_path)
        self.transforms = album.Compose(
            transforms=[
                album.Resize(442, 572, always_apply=True),
                EnsureLandscape(always_apply=True),
                album.Normalize(),
                ToTensorV2(),
            ]
        )

    def detect(self, image):
        image = self._transform(image, self.transforms)
        prediction = self._predict(self.model, image)
        return prediction

    def _transform(self, image):
        return self.transforms(np.asarray(image))["image"].unsqueeze(0)

    def _predict(self, image):
        return self.model(image)

    def _load_model(self, model_path):
        model = PhilTableDetection.load_from_checkpoint(model_path)
        model.eval()
        model.requires_grad_(False)
        return model


# def detect(pdf_path, output_path):
#     pages = convert_from_path(pdf_path)
#     detector = Detector(MODEL_PATH)
#     for page in pages:
#         prediction = detector.detect(page)
#         if prediction:
#             page.save(output_path)

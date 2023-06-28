import albumentations as album
import numpy as np
from albumentations.pytorch.transforms import ToTensorV2


class EnsureLandscape(album.ImageOnlyTransform):
    def __init__(self, always_apply=False, p=1.0):
        super(EnsureLandscape, self).__init__(always_apply, p)

    def apply(self, img, **params):
        if img.shape[0] > img.shape[1]:
            img = np.rot90(img)
        return img

    def get_transform_init_args_names(self):
        return ()


# preserve aspect ratio from original image size (1700, 2200)
# but resize to a smaller size for faster training
DEFAULT_TRANSFORMS = album.Compose(
    transforms=[
        album.Resize(442, 572, always_apply=True),
        EnsureLandscape(always_apply=True),
        album.Normalize(),
        ToTensorV2(),
    ]
)

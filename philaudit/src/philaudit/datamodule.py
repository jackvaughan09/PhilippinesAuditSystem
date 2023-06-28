from typing import Union

import albumentations as album
import numpy as np
import pytorch_lightning as pl
import torch
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision.datasets import ImageFolder

from .transforms import DEFAULT_TRANSFORMS


# Implementing a custom dataset with a __getitem__ method allows us to apply
# transforms upon image retrieval. Saves us from having to load the entire
# dataset to memory to apply the transforms in one go.
class PhilImageDataset(Dataset):
    def __init__(
        self, data, transforms: Union[album.Compose, None] = DEFAULT_TRANSFORMS
    ):
        self.data = data
        self.transforms = transforms

    def __len__(self):
        """Dataset Length."""
        return len(self.data)

    def __getitem__(self, idx):
        image, label = self.data[idx]
        image = np.asarray(image)
        if self.transforms:
            image = self.transforms(image=image)["image"]
        return image, label


class PhilDataModule(pl.LightningDataModule):
    def __init__(
        self,
        data_root,
        num_workers=2,
        batch_size=16,
        val_split=0.2,
        test_split=0.1,
        seed=42,
        transforms=None,
    ):
        super().__init__()
        self.data_root = data_root
        self.batch_size = batch_size
        self.val_split = val_split
        self.test_split = test_split
        self.seed = seed
        self.num_workers = num_workers
        self.transforms = transforms

    def setup(self, stage=None):
        train_set, val_set, test_set = self._get_dataset_splits()
        self.train_set = PhilImageDataset(train_set, transforms=self.transforms)
        self.val_set = PhilImageDataset(val_set, transforms=self.transforms)
        self.test_set = PhilImageDataset(test_set, transforms=self.transforms)

    def _get_dataset_splits(self):
        dataset = ImageFolder(root=self.data_root)

        val_size = int(self.val_split * len(dataset))
        test_size = int(self.test_split * len(dataset))
        train_size = len(dataset) - val_size - test_size

        torch.manual_seed(self.seed)

        return random_split(dataset, [train_size, val_size, test_size])

    def train_dataloader(self):
        return DataLoader(
            self.train_set,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
        )

    def val_dataloader(self):
        return DataLoader(
            self.val_set,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

    def test_dataloader(self):
        return DataLoader(
            self.test_set,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
        )

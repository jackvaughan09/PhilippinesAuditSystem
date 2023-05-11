import albumentations as album
import pytorch_lightning as pl
from albumentations.pytorch.transforms import ToTensorV2
from model import PhilTableDetection
from phildata import EnsureLandscape, PhilDataModule
from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint
from pytorch_lightning.loggers import TensorBoardLogger

# Use the following line during tensor core GPU training
# torch.set_float32_matmul_precision("medium")

if __name__ == "__main__":
    data_root = "./training_data/"
    checkpointdir = "./checkpoints/"
    logdir = "./tb_logs/"
    # preserve aspect ratio from original image size (1700, 2200)
    # but resize to a smaller size for faster training
    resized_image_size = (442, 572)

    transforms = album.Compose(
        transforms=[
            album.Resize(*resized_image_size, always_apply=True),
            EnsureLandscape(always_apply=True),
            album.Normalize(),
            ToTensorV2(),
        ]
    )

    datamodule = PhilDataModule(
        data_root=data_root, num_workers=12, batch_size=16, transforms=transforms
    )

    # Create the model with the suggested hyperparameters
    model = PhilTableDetection(
        num_classes=1,
        learning_rate=0.000023135,
        dropout_rate=0,
        num_filters1=64,
        num_filters2=128,
        num_fc_nodes=128,
    )

    callbacks = [
        EarlyStopping(monitor="val_prec", min_delta=0.01, patience=3),
        EarlyStopping(monitor="val_loss", min_delta=0.01, patience=3),
        ModelCheckpoint(
            dirpath=checkpointdir,
            monitor="val_prec",
            save_top_k=1,
            filename="{epoch}-{val_loss:.2f}-{val_prec:.2f}-{val_acc:.2f}-{val_rec:.2f}",
            mode="min",
            every_n_epochs=3,
        ),
    ]

    EXPERIMENT_NAME = f"{model.__class__.__name__}"
    logger = TensorBoardLogger(save_dir=logdir, name=EXPERIMENT_NAME)

    # Train the model
    trainer = pl.Trainer(
        max_epochs=10,  # Adjust this to your needs
        accelerator="cpu",
        logger=logger,
        enable_model_summary=True,
        enable_progress_bar=True,
        callbacks=callbacks,
    )
    trainer.fit(model, datamodule=datamodule)

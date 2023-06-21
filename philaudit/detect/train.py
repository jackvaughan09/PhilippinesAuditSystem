from typing import List, Union

import optuna
import pytorch_lightning as pl
from pytorch_lightning.loggers import TensorBoardLogger

from philaudit.detect.datamodule import PhilDataModule
from philaudit.detect.model import PhilTableDetection
from philaudit.detect.callbacks import get_callbacks
from philaudit.detect.transforms import DEFAULT_TRANSFORMS

# Use the following line during tensor core GPU training
# torch.set_float32_matmul_precision("medium")


def objective(
    trial,
    data_root: str,
    num_workers: int = 2,
    batch_size: int = 16,
    model_ckpt: Union[str, None] = None,
    ckpt_dir: Union[str, None] = None,
    experiment_name: Union[str, None] = None,
    max_epochs: int = 5,
    accelerator: str = "cpu",
    log_dir: Union[str, None] = None,
    callbacks: Union[List, None] = None,
    transforms: List = DEFAULT_TRANSFORMS,
):
    """The objective function to be optimized by Optuna.
    Review this code for specifics on the default search space.

    You will probably need to adjust the num_workers and batch_size
    for the dataloader used here, as well as the number of trials to run.

    It is possible to start the model from a past training checkpoint,
    though in my experience, this method is particularly prone to overfitting.


    Args:
        trial (optuna.Trial): The current trial to be evaluated.
    Returns:
        float: The validation loss of the model.
    """

    datamodule = PhilDataModule(
        data_root=data_root,
        num_workers=num_workers,
        batch_size=batch_size,
        transforms=transforms,
    )

    if model_ckpt:
        model = PhilTableDetection().load_from_checkpoint(model_ckpt)
    else:
        model = PhilTableDetection()

    if not experiment_name:
        experiment_name = f"{model.__class__.__name__}"
    if not callbacks:
        callbacks = get_callbacks(checkpoint_dir=ckpt_dir)

    logger = TensorBoardLogger(save_dir=log_dir, name=experiment_name)

    # Train the model
    trainer = pl.Trainer(
        max_epochs=max_epochs,  # Adjust this to your needs
        accelerator=accelerator,
        logger=logger,
        enable_model_summary=True,
        enable_progress_bar=True,
        callbacks=callbacks,
    )
    trainer.fit(model, datamodule=datamodule)
    return trainer.logged_metrics["val_loss"]


if __name__ == "__main__":
    # TODO: Add argparse for these
    data_root = "./training_data/"
    checkpointdir = "./checkpoints/"
    log_dir = "./tb_logs/"
    checkpoint = None
    n_trials = 5

    my_objective = objective()

    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

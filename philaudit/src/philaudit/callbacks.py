from pytorch_lightning.callbacks import EarlyStopping, ModelCheckpoint


def get_callbacks(checkpointdir):
    [
        EarlyStopping(monitor="val_prec", min_delta=0.005, patience=3),
        EarlyStopping(monitor="val_loss", min_delta=0.005, patience=3),
        ModelCheckpoint(
            dirpath=checkpointdir,
            monitor="val_loss",
            save_top_k=1,
            filename="{epoch}-{val_loss:.2f}-{val_prec:.2f}-{val_acc:.2f}-{val_rec:.2f}",
            mode="min",
            every_n_epochs=3,
        ),
    ]

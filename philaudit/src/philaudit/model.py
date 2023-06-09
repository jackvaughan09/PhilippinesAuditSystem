import pytorch_lightning as pl
import torch
from torch import nn, optim
from torchmetrics import Accuracy, Precision, Recall


class PhilTableDetection(pl.LightningModule):
    """PhilTableDetection

    PyTorch Lightning Module for the PhilImages dataset. Handles the model
    architecture, training, validation, and testing. Class has been created
    to be flexible to allow for hyperparameter tuning with Optuna.

    Args:
        num_classes (int, optional): Number of classes in the dataset.
            Defaults to 1.
        learning_rate (float, optional): Learning rate for the optimizer.
            Defaults to 1e-4.
        weight_decay (float, optional): Weight decay for the optimizer.
            Defaults to 0.
        dropout_rate (float, optional): Dropout rate for the dropout layers.
            Defaults to 0.
        num_filters1 (int, optional): Number of filters for the first
            convolutional layer. Defaults to 16.
        num_filters2 (int, optional): Number of filters for the second
            convolutional layer. Defaults to 32.
        padding (int, optional): Padding for the convolutional layers.
            Defaults to 1.
        stride (int, optional): Stride for the convolutional layers.
            Defaults to 1.
        filter_size (int, optional): Filter size for the convolutional layers.
            Defaults to 3.
        num_fc_nodes (int, optional): Number of nodes for the fully connected
            layer. Defaults to 64.
        image_size (tuple, optional): Size of the input images. Defaults to
            (442, 572).

    Returns:
        PhilTableDetection: PyTorch Lightning Module for the PhilImages dataset.
    """

    def __init__(
        self,
        num_classes=1,
        learning_rate=1e-4,
        weight_decay=0,
        dropout_rate=0,
        num_filters1=16,
        num_filters2=32,
        padding=1,
        stride=1,
        filter_size=3,
        num_fc_nodes=64,
        image_size=(442, 572),
    ):
        super().__init__()
        self.save_hyperparameters()
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.dropout_rate = dropout_rate
        self.num_filters1 = num_filters1
        self.num_filters2 = num_filters2
        self.num_fc_nodes = num_fc_nodes
        self.padding = padding
        self.stride = stride
        self.filter_size = filter_size
        self.image_size = image_size

        # Adjust padding to be (filter_size - 1) / 2 for 'same' padding
        self.padding = (self.filter_size - 1) // 2

        self.loss_function = nn.BCEWithLogitsLoss()
        self.acc = Accuracy(task="binary").to(self.device)
        self.rec = Recall(task="binary").to(self.device)
        self.prec = Precision(task="binary").to(self.device)

        self.conv1 = nn.Conv2d(
            3,
            self.num_filters1,
            self.filter_size,
            stride=self.stride,
            padding=self.padding,
        )
        self.rel1 = nn.ReLU()
        self.bn1 = nn.BatchNorm2d(self.num_filters1)
        self.pool1 = nn.MaxPool2d(2, 2)
        self.dropout1 = nn.Dropout(self.dropout_rate)

        self.conv2 = nn.Conv2d(
            self.num_filters1,
            self.num_filters2,
            self.filter_size,
            stride=self.stride,
            padding=self.padding,
        )
        self.rel2 = nn.ReLU()
        self.bn2 = nn.BatchNorm2d(self.num_filters2)
        self.pool2 = nn.MaxPool2d(2, 2)
        self.dropout2 = nn.Dropout(self.dropout_rate)

        self.fc1 = nn.Linear(self._calculate_linear_input_size(), self.num_fc_nodes)
        self.rel3 = nn.ReLU()
        self.dropout3 = nn.Dropout(self.dropout_rate)

        self.fc2 = nn.Linear(self.num_fc_nodes, self.num_classes)

    def _calculate_linear_input_size(self):
        # Pass a dummy input through the convolutional and pooling layers
        # to dynamically calculate the input size to the fully connected layer
        x = torch.zeros(1, 3, *self.image_size)
        x = self.dropout1(self.pool1(self.bn1(self.rel1(self.conv1(x)))))
        x = self.dropout2(self.pool2(self.bn2(self.rel2(self.conv2(x)))))
        return x.numel()

    def forward(self, x):
        x = self.dropout1(self.pool1(self.bn1(self.rel1(self.conv1(x)))))
        x = self.dropout2(self.pool2(self.bn2(self.rel2(self.conv2(x)))))
        x = x.view(x.size(0), -1)  # Flatten the input tensor
        x = self.dropout3(self.rel3(self.fc1(x)))
        x = self.fc2(x)
        return x

    def training_step(self, batch, batch_idx):
        inputs, targets = batch
        inputs.to(self.device), targets.to(self.device)
        logits = self(inputs)  # logits get turned to HalfTensor so vvv
        loss = self.loss_function(logits.view(-1), targets.to(logits.dtype))
        return loss

    def validation_step(self, batch, batch_idx):
        inputs, targets = batch
        inputs.to(self.device), targets.to(self.device)
        logits = self(inputs)
        loss = self.loss_function(logits.view(-1), targets.to(logits.dtype))
        preds = (torch.sigmoid(logits.view(-1)) > 0.5).type(torch.FloatTensor)

        acc = self.acc(preds, targets.type(torch.FloatTensor))
        rec = self.rec(preds, targets.type(torch.FloatTensor))
        prec = self.prec(preds, targets.type(torch.FloatTensor))

        self.log_dict(
            {"val_loss": loss, "val_acc": acc, "val_prec": prec, "val_recall": rec},
            prog_bar=True,
        )

    def test_step(self, batch, batch_idx):
        inputs, targets = batch
        inputs.to(self.device), targets.to(self.device)
        logits = self(inputs)
        loss = self.loss_function(logits.view(-1), targets.to(logits.dtype))
        preds = (torch.sigmoid(logits.view(-1)) > 0.5).type(torch.FloatTensor)

        acc = self.acc(preds, targets.type(torch.FloatTensor))
        rec = self.rec(preds, targets.type(torch.FloatTensor))
        prec = self.prec(preds, targets.type(torch.FloatTensor))

        self.log_dict(
            {"val_loss": loss, "val_acc": acc, "val_prec": prec, "val_recall": rec},
            prog_bar=True,
        )

    def configure_optimizers(self):
        optimizer = optim.Adam(
            self.parameters(), lr=self.learning_rate, weight_decay=self.weight_decay
        )
        return optimizer

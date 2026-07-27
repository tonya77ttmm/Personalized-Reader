from torch import nn
class EmotionMLP(nn.Module):
    def __init__(self, input_size, hidden_layers, dropout_rate, num_classes=2):
        super().__init__()

        layers = []
        in_dim = input_size

        for h in hidden_layers:
            layers += [
                nn.Linear(in_dim, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout_rate)
            ]
            in_dim = h

        layers.append(nn.Linear(in_dim, num_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)
import torch.nn as nn

class PoseMLP(nn.Module):
    def __init__(self, input_dim = 135, hidden_dim1 = 128, hidden_dim2 = 64, dropout = 0.2, output_dim = 1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(),
            nn.Dropout(dropout),


            nn.Linear(hidden_dim1, hidden_dim2),
            nn.BatchNorm1d(hidden_dim2),
            nn.ReLU(),
            nn.Dropout(dropout),

            nn.Linear(hidden_dim2, output_dim)
        )
    
    def forward(self, x):
        return self.net(x).squeeze(-1)
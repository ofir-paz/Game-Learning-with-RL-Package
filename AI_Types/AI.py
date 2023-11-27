"""

"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class AI(nn.Module):

    def __init__(self, in_features, out_features):
        super(AI, self).__init__()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.fc1 = nn.Linear(in_features, 32)
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, out_features)
        self.to(self.device)

    def forward(self, x: torch.tensor):
        x = x.to(self.device)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x

    def predict(self, x):
        x = torch.tensor(x)
        x_orig_device = x.device
        x = self.forward(x)
        x.to(x_orig_device)

        return int(torch.argmax(x))

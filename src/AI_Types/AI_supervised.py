
import torch
from torch.utils.data import Dataset, DataLoader
from src.AI_Types.AI import AI


def load_dataset(infos, actions, batch_size=2048):
    class BallGameDataset(Dataset):
        def __init__(self, inputs, labels):
            self.inputs = inputs
            self.labels = labels

        def __len__(self):
            return len(self.inputs)

        def __getitem__(self, index):
            input = torch.tensor(self.inputs[index])
            label = torch.tensor(self.labels[index])

            return input, label

    dataset = BallGameDataset(infos, actions)
    dataset_loader = DataLoader(dataset, batch_size, shuffle=True)

    return dataset_loader


def define_optimizers(model: AI, lr=0.001):
    loss_func = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    return loss_func, optimizer


def fit(model: AI, train_loader: DataLoader, batch_size, lr=0.001, num_epochs=10,
        print_cost=False, print_stride=1):
    loss_func, optimizer = define_optimizers(model, lr=lr)

    for epoch in range(num_epochs):
        running_loss = 0.
        for i, mini_batch in enumerate(train_loader):
            # get the inputs; data is a list of [inputs, labels]
            inputs, labels = mini_batch
            inputs = inputs.to(model.DEVICE)
            labels = labels.to(model.DEVICE)

            # zero the parameter gradients
            optimizer.zero_grad()

            # forward + backward + optimize
            predicts = model(inputs)

            loss = loss_func(predicts, labels)
            loss.backward()
            optimizer.step()

            # Calc loss
            lloss = loss.item()

            if print_cost:
                running_loss += lloss * inputs.size(0)
                print(f"\r[epoch: {epoch+1} MB: {i+1}] Loss: {lloss}", end='')

        if print_cost and epoch % print_stride == 0:
            epoch_loss = running_loss / (len(train_loader) * batch_size)
            print(f"\r[epoch: {epoch + 1}] Total Loss: {epoch_loss}")


def train_ai(infos, actions, batch_size=2048, lr=0.001, num_epochs=10,
             print_cost=False, print_stride=1):

    train_loader = load_dataset(infos, actions, batch_size)
    ai = AI(2, 3)
    fit(ai, train_loader, batch_size, lr, num_epochs, print_cost, print_stride)
    ai.eval()

    return ai

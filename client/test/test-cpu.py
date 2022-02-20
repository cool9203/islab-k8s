import torch
from torch import nn
from tqdm import tqdm


print(f"use GPU:{torch.cuda.is_available()} in init")


class NET(nn.Module):
    def __init__(self, batch_size, class_num):
        super(NET, self).__init__()
        self.conv1d_1 = nn.Conv1d(1, 1, 3, padding=1)
        self.max_pool_1 = nn.MaxPool1d(2, padding=1)
        self.conv1d_2 = nn.Conv1d(1, 1, 3, padding=1)
        self.max_pool_2 = nn.MaxPool1d(2, padding=1)
        self.dense_1 = nn.Linear(2, 512)
        self.dense_2 = nn.Linear(512, 256)
        self.dense_3 = nn.Linear(256, 128)
        self.output_layer = nn.Linear(128, class_num)

  
    def forward(self, sentence):
        x = torch.mean(sentence, 1, True)
        x = self.conv1d_1(x)
        x = self.max_pool_1(x)
        x = self.conv1d_2(x)
        x = self.max_pool_2(x)
        x = self.dense_1(x)
        x = self.dense_2(x)
        x = self.dense_3(x)
        outputs = self.output_layer(x)
        return outputs


def train(epochs, net, x, y):
    device = torch.device("cpu")
    print(f"use GPU:{torch.cuda.is_available()} in train")
    print(f"use device:{device}")
    
    net.train()
    net.to(device)
    x = x.to(device)
    y = y.to(device)

    # 使用 Adam Optim 更新整個分類模型的參數
    optimizer = torch.optim.Adam(net.parameters(), lr=1e-5)
    loss_func = torch.nn.MSELoss()

    for epoch in tqdm(range(epochs)):
        optimizer.zero_grad()
        output = net(x)
        loss = loss_func(output, y)
        loss.backward()
        optimizer.step()


def main():
    BATCH_SIZE = 1
    EPOCHS = 999999
    net = NET(BATCH_SIZE, 1)

    x = torch.tensor([
                [[1,2,3,4], [2,3,4,5]],
                [[1,2,3,4], [1,2,3,4]],
                [[1,2,3,4], [2,3,4,5]],
                [[1,2,3,4], [1,2,3,4]]
              ], dtype=torch.float)

    y = torch.tensor([1, 2, 1, 2], dtype=torch.float)

    train(EPOCHS, net, x, y)


if (__name__ == "__main__"):
    main()

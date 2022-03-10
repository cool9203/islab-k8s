"""
islab gpu 範例訓練程式
請配合main.py一起觀看，才能正常使用
這邊使用套件為pytorch，若要要用其他主流框架，請注意意下幾個撰寫重點

1. 訓練代數請使用自行指定的最大代數+islab.get_train_epoch() 來控制訓練代數
2. 訓練一代完請使用islab.add_train_epoch(epoch) 來增加已訓練代數，其中epoch為當前代數，會記錄成epoch+1
3. 請將訓練包成一個function，並使用在外面加上@islab.register，否則是不會去租借GPU下來使用的
4. 請注意，若你資料需要打亂順序，請將資料先打亂過後儲存起來，否則寫在這程式裡，訓練的資料順序可能不會一樣
"""


from pathlib import Path
import sys
sys.path.insert(0, str(Path("../").resolve()))
import islab_gpu as islab


@islab.register     #這行與train function請則一添加，若一起寫到也沒關係
def main():
    import torch
    from torch import nn
    from tqdm import tqdm   # 進度條，若你框架允許，這lib還不錯用，推薦


    print(f"use GPU:{torch.cuda.is_available()} in init")

    # pytorch定義網路的部分
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

    # 實際訓練的function
    @islab.register
    def train(epochs, net, x, y):
        train_epoch = islab.get_train_epoch()       # 一定要寫到，否則代數會每次都重新計算
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print(f"use GPU:{torch.cuda.is_available()} in train")
        print(f"use device:{device}")
        
        net.train()
        net.to(device)
        x = x.to(device)
        y = y.to(device)

        # 使用 Adam Optim 更新整個分類模型的參數
        optimizer = torch.optim.Adam(net.parameters(), lr=1e-5)
        loss_func = torch.nn.MSELoss()

        for epoch in tqdm(range(train_epoch, epochs)):
            optimizer.zero_grad()
            output = net(x)
            loss = loss_func(output, y)
            loss.backward()
            optimizer.step()
            islab.add_train_epoch(epoch)            # 一定要寫到，否則增加過後的代數不會被記錄起來

    BATCH_SIZE = 1
    TARGET_EPOCH = islab.get_max_epoch()    # 可寫可不寫，但不使用function的話，這邊最大代數需要設定與main.py一樣
    net = NET(BATCH_SIZE, 1)

    x = torch.tensor([
                [[1,2,3,4], [2,3,4,5]],
                [[1,2,3,4], [1,2,3,4]],
                [[1,2,3,4], [2,3,4,5]],
                [[1,2,3,4], [1,2,3,4]]
              ], dtype=torch.float)

    y = torch.tensor([1, 2, 1, 2], dtype=torch.float)

    train(TARGET_EPOCH, net, x, y)


if (__name__ == "__main__"):
    main()

"""
islab gpu example

該程式為主呼叫程式，請根據這程式修改為你的版本。

該程式有幾個撰寫重點:
1. islab.get_train_epoch 這function一定要記得呼叫，並埋在while裡，否則epoch不會更新，會讓程式無限訓練下去
2. islab.reset_train_epoch 這function一定要寫到，除非你呼叫目的為接續訓練，否則當前這程式可訓練到指定代數才對。
3. p = subprocess.Popen("python YOUR_TRAIN_PROGRAM_FILE_NAME.py", shell=True) 利用這程式呼叫你訓練程式。
4. p.wait()一定要寫到，否則你程式會無限制的一直叫訓練程式。
"""


from pathlib import Path
import sys
sys.path.insert(0, str(Path("../").resolve()))
import islab_gpu as islab
import subprocess

target_epoch = 999999
epoch = 0
islab.reset_train_epoch()
islab.set_max_epoch(target_epoch)
while (epoch <= target_epoch):
    print(f"epoch:{epoch}")
    p = subprocess.Popen("python3 test-gpu.py", shell=True)
    p.wait()
    epoch = islab.get_train_epoch()


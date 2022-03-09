from pathlib import Path
import sys
sys.path.insert(0, str(Path("../").resolve()))
import islab_gpu as islab
import subprocess

target_epoch = 999999
epoch = 0
islab.reset_train_epoch()
while (epoch <= target_epoch):
    print(f"epoch:{epoch}")
    p = subprocess.Popen("python3 test-gpu.py", shell=True)
    p.wait()
    epoch = islab.get_train_epoch()


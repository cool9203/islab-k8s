#! python3
# coding: utf-8

from functools import wraps
import time
import os, platform
from urllib.parse import urljoin
import requests
import json
from pathlib import Path

import logging
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler = logging.FileHandler("/root/data/islab_gpu.log", mode="w", encoding="utf8")
handler.setFormatter(formatter)
logger.addHandler(handler)


__api_host = "http://203.64.95.118"
__api_port = "30001"
__api_url = f"{__api_host}:{__api_port}"
__version__ = "20220308"
__author__ = "yoga, email:octer18@gmail.com"    #有問題請聯絡
___train_epoch_data_path = "/root/data/.train_epoch.txt"
___max_epoch_data_path = "/root/data/.max_epoch.txt"


"""
動態修改api host
"""
def set_api_host(api_host):
    __api_host = api_host
    __api_url = __get_api_url()


"""
動態修改api port
"""
def set_api_port(api_port):
    __api_port = api_port
    __api_url = __get_api_url()


"""
取得GPU可使用的剩餘時間，格式為hh:mm:ss
"""
def get_remain_time():
    data = __call_api("GET")
    return str(data["time"])


"""
取得GPU狀態:
1. NONE: 不在GPU排隊對列裡
2. WAIT: 在GPU排隊對列裡
3. START: 已取得GPU，可開始使用
"""
def get_status():
    data = __call_api("GET")
    return data["gpu_status"]


"""
由於上層管理的軟體會直接讓python結束，所以需要配合特定寫法來讓訓練程式可以訓練到指定代數。
其中若曾租借過，但使用時間到，但要接續訓練時，代數需要接著訓練，所以這func可以取得用add_train_epoch紀錄的代數。
"""
def get_train_epoch():
    try:
        with Path(___train_epoch_data_path).open("r") as f:
            try:
                epoch = int(f.readline().replace("\n", "").replace("\t", "").replace("\r", ""))
            except Exception as e:
                epoch = 0
    except Exception as e:
        reset_train_epoch()
        epoch = 0
    return epoch


"""
配合get_train_epoch，可epoch++，並記錄在指定檔案裡。
"""
def add_train_epoch(epoch=None):
    if (epoch is None):
        epoch = get_train_epoch()

    with Path(___train_epoch_data_path).open("w") as f:
        f.write(str(epoch+1))


"""
主呼叫程式請一定要使用，否則會讓epoch不會重置。
"""
def reset_train_epoch():
    with Path(___train_epoch_data_path).open("w") as f:
        f.write(str(0))


"""
設定最大代數
"""
def set_max_epoch(max_epoch):
    with Path(___max_epoch_data_path).open("w") as f:
        f.write(str(max_epoch))


"""
取得設定好的最大代數
"""
def get_max_epoch():
    try:
        with Path(___max_epoch_data_path).open("r") as f:
            try:
                max_epoch = int(f.readline().replace("\n", "").replace("\t", "").replace("\r", ""))
            except Exception as e:
                max_epoch = 0
    except Exception as e:
        set_max_epoch(0)
        raise Exception("you should set max epoch with function 'set_max_epoch(max_epoch)'")
    return max_epoch


"""
測試用func，若連接不上可使用這func，可得到上層系統是否正常。
"""
def test():
    data = __call_api("GET")
    return True


"""
租借GPU
"""
def register(func):
    @wraps(func)    #註冊reutrn的func，將func的屬性抄到return的func裡
    def new_func(*args ,**kwargs):
        #申請GPU
        try:
            while (get_status() in ["NONE", "DELETE"]):
                __mount_gpu()
            logger.info("add gpu queue success")
        except KeyboardInterrupt:
            if get_status() == "START":
                __unmount_gpu()
                logger.info("remove gpu queue success")
        try:
            while (get_status() != "START"):
                time.sleep(2)
            logger.info("mount gpu success")

            #實際執行的func
            result = func(*args ,**kwargs)
            #歸還GPU
            __unmount_gpu()
            logger.info("remove gpu queue success")
        #當使用者手動中斷時會自動歸還
        except KeyboardInterrupt:            
            #歸還GPU
            __unmount_gpu()
            logger.info("remove gpu queue success")
        return result
    return new_func


def __mount_gpu():
    __call_api("ADD")


def __unmount_gpu():
    __call_api("REMOVE")


def get_hostname():
    if (platform.system().lower() == "windows"):
        return platform.uname().node
    return os.uname()[1]


"""
requests format:
    1. 失敗:
        {
            status:"unsuccess"
        }
    2. 成功:
        {
            status:"success"
            #以下是GET會多的資料
            gpu_status:"START/WAIT/NONE",   #分別代表 已取得GPU/在GPU對列等待中/不在GPU對列裡
            time:datetime.deltatime,        #代表GPU剩餘可用時間，需要加上str轉型，格式為hh:mm:ss。其中若剩餘時間為小時以上的單位時，hh會超過24
            queue_index:int                 #在對列裡的index
        }
"""
def __call_api(action):
    if (not action in ["ADD", "REMOVE", "GET"]):
        raise Exception("action error")
    
    hostname = get_hostname()
    data = {"name":hostname, "token":""}
    headers = {"Content-Type": "application/json"}

    logger.info(data)
    api_url = f"{__api_url}/gpu/{action}"
    req = requests.post(api_url, data=json.dumps(data), headers=headers)
    response_data = json.loads(req.text)

    if (response_data["status"] == "unsuccess"):
        logger.info(f"__api_url : {__api_url}")
        logger.info(response_data)
        raise Exception(f"please contact {__author__}")

    return response_data


"""
使用範例:
step 1. import這隻程式
step 2. 在要訓練或主要呼叫的程式加上@register，即可自動申請GPU至VM上

實際範例:
import islab_gpu as islab

@islab.register
def main():
    print("模型訓練")
"""

@register
def main():
    """
    unit test and example
    """
    print("模型訓練")

    import os
    os.system("nvidia-smi -L")
    time.sleep(15)


if (__name__ == "__main__"):
    main()
    input("press key of enter to continue...")

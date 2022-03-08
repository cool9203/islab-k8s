#! python3
# coding: utf-8

from functools import wraps
import time
import os, platform
from urllib.parse import urljoin
import requests
import json

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
__author__ = "yoga, email:octer18@gmail.com"


"""
"""
def set_api_version(api_version):
    __api_version = api_version
    __api_url = __get_api_url()


"""
"""
def set_api_host(api_host):
    __api_host = api_host
    __api_url = __get_api_url()


"""
"""
def set_api_port(api_port):
    __api_port = api_port
    __api_url = __get_api_url()


def get_remain_time():
    data = __call_api("GET")
    return str(data["time"])


def get_status():
    data = __call_api("GET")
    return data["gpu_status"]


def test():
    data = __call_api("GET")
    return True


def register(func):
    @wraps(func)    #註冊reutrn的func，將func的屬性抄到return的func裡
    def new_func(*args ,**kwargs):
        #申請GPU
        while (get_status() in ["NONE", "DELETE"]):
            __mount_gpu()
        logger.info("add gpu queue success")

        while (get_status() != "START"):
            time.sleep(2)
        logger.info("mount gpu success")

        #實際執行的func
        result = func(*args ,**kwargs)

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

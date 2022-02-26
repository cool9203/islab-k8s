import logging

logger = logging.getLogger(__name__)

import json
import threading
import datetime as dt
import time
import pkg.kubeapi
import pkg.dbapi


class _manager(threading.Thread):
    def __init__(self, sleep_time_s = 4):
        threading.Thread.__init__(self)
        self.kubeapi = pkg.kubeapi._kubeapi()
        self.sleep_time_s = sleep_time_s                # 幾秒跑一次run function
        self.queue = dict()                             # 因為重開後所有pod都會重來，所以應該要是空的
        self.max_gpu_count = dict()                     # GPU數量最大值
        self.running = dict()                           # 正在使用的GPU數量
        self.uid = 0                                    # 每一個申請者對應到的申請id
        self.signal = True                              # 是否要繼續執行run function
        self.time_format = "%Y/%m/%d %H:%M:%S"          # datetime format
        self.default_delta_time = {                     # 控制掛載後的卸載時間，days可以填365以上，他會自動計算
            "weeks": 0,
            "days": 0,
            "hours": 3,
            "minutes": 0,
            "seconds": 0
        }
        self.add_lock = False                           # add鎖，以防同時間有複數人要加入

        logger.debug(f"now use queue : {self.queue}")
        logger.debug(f"now use uid : {self.uid}")
        logger.debug(f"now use max_gpu_count : {self.max_gpu_count}")
        logger.debug(f"now use running : {self.running}")

    def _add_all_node(self):
        node_list = self.kubeapi.get_all_node()
        for node_name, node_status in node_list.items():
            if (not node_name in self.queue):
                self.queue[node_name] = dict()
                self.max_gpu_count[node_name] = node_status["gpu"]
                self.running[node_name] = 0

    def __get_all_name_list(self, node_name):
        all_name_list = list()
        for uid, data in self.queue[node_name].items():
            all_name_list.append(data["name"])
        return all_name_list

    def get_uid_list(self, node_name):
        return sorted(self.queue[node_name].keys())

    def __get_uid_with_name(self, node_name, pod_name):
        uid_list = self.get_uid_list(node_name)
        for uid in uid_list:
            if (self.queue[node_name][uid]["name"] == pod_name):
                return uid
        raise Exception(f"pod_name: {pod_name} not in gpu queue.")

    def add(self, node_name, pod_name, delta_time=None):
        while(self.add_lock):
            pass
        self.add_lock = True

        if (not node_name in self.queue.keys()):
            logger.info(f"pod:'{node_name}' not in cluster. so add gpu queue failed.")
            return False

        all_name_list = self.__get_all_name_list(node_name)
        all_pod_name_list = self.kubeapi.get_all_pod().keys()

        if (pod_name in all_name_list):
            logger.info(f"pod:'{node_name}/{pod_name}' already exists in gpu queue, so add failed.")
            self.add_lock = False
            return False

        elif (not pod_name in all_pod_name_list):
            logger.info(f"pod:'{node_name}/{pod_name}' not in cluster or not running. so add gpu queue failed.")
            self.add_lock = False
            return False

        else:
            logger.info(f"pod:'{node_name}/{pod_name}' add gpu queue success.")
            self.queue[node_name][int(self.uid)] = {"status":"WAIT", "start_time":"", "end_time":"", "name":pod_name, "delta_time":delta_time}
            self.uid = int(self.uid) + 1
            self.add_lock = False
            return True

    def remove(self, node_name, pod_name):
        try:
            uid = self.__get_uid_with_name(node_name, pod_name)
            if (self.queue[node_name][uid]["status"] == "START"):
                self.queue[node_name][uid]["status"] = "DELETE"
            else:
                self.queue[node_name][uid]["status"] = "DELETE"
                pkg.dbapi.add_log({"name":f"{node_name}/{pod_name}", "status":"DELETE", "start_time":self.queue[uid]["start_time"], "end_time":self.queue[uid]["end_time"]})
                del self.queue[node_name][uid]
        except Exception as e:
            logger.error(e)
        return True

    def get(self, node_name, pod_name):
        try:
            uid = self.__get_uid_with_name(node_name, pod_name)
            status = self.queue[node_name][uid]["status"]

            if (len(self.queue[node_name][uid]["start_time"]) == 0):                                        #尚未開始
                remain_time = ""
            elif (self.get_time(self.queue[node_name][uid]["end_time"]) < self.get_time(self.get_time())):  #時間到，但還沒被管理程式結束，所以有可能隨時結束
                remain_time = "00:00:00"
            else:                                                                                           #正在執行，需要回傳剩餘時間
                remain_time = str(self.get_time(self.queue[node_name][uid]["end_time"]) - self.get_time(self.get_time()))

            queue_index = self.get_uid_list(node_name).index(uid) - self.running[node_name] + 1
            return {"gpu_status":status, "time":remain_time, "queue_index":queue_index}
        except Exception as e:
            logger.error(e)
        return {"gpu_status":"NONE", "time":"", "queue_index":""}

    """
    這邊的概念是只卸載1個pod上的GPU，所以在unmount時只要卸載到就break，並且掛載一個上去
    會這樣做主要是因為若當前排隊數量是max_gpu_count+1時，若把當前該卸載的全卸載掉，會空閒max_gpu_count-1張卡下來，所以寧願一次卸一張掛一張，讓重複執行去做掛與卸
    """
    def __check(self, node_name, unmount=False):
        uid_list = self.get_uid_list(node_name)
        rotation = False
    
        #先卸載自己要結束的
        for uid in uid_list:
            if (self.queue[node_name][uid]["status"] in ["DELETE"] and
                    len(self.queue[node_name][uid]["end_time"]) > 0):
                self.__unmount(node_name, uid)

        #先卸載該結束的
        if (unmount):
            for uid in uid_list:
                if (self.queue[node_name][uid]["status"] in ["START"] and 
                        len(self.queue[node_name][uid]["end_time"]) > 0 and
                        self.get_time(self.queue[node_name][uid]["end_time"]) <= self.get_time(self.get_time())):
                    self.queue[node_name][uid]["status"] = "END"
                    self.__unmount(node_name, uid)
                    break

        #掛載新的
        uid_list = self.get_uid_list(node_name)
        for uid in uid_list:
            if (self.running[node_name] == self.max_gpu_count[node_name]):
                break
            else:
                if (self.queue[node_name][uid]["status"] == "WAIT"):
                    if (self.__mount(node_name, uid)):
                        rotation = True
                        break
        return rotation

    def __unmount(self, node_name, uid):
        try:
            name = self.queue[node_name][uid]["name"]
            pkg.dbapi.add_log({"name":f"{node_name}/{pod_name}", "status":"DELETE", "start_time":self.queue[uid]["start_time"], "end_time":self.queue[uid]["end_time"]})
            del self.queue[node_name][uid]

            ret = self.kubeapi.remove_gpu_to_pod(name)
            logger.debug(f"unmount uid : {uid}, {name}")

            if (ret):
                self.running[node_name] -= 1
                return True
            else:
                return False

        except Exception as e:
            logger.error(e)
            logger.debug(f"uid:{uid} unmount gpu failed. so restart pod")
            self.kubeapi._delete_pod(name)
            self.kubeapi._apply_pod(name)
            self.running[node_name] -= 1
            return True

    def __mount(self, node_name, uid):
        if (not self.queue[node_name][uid]["status"] in ["WAIT"]):
            return True

        try:
            name = self.queue[node_name][uid]["name"]
            logger.debug(f"mount uid : {uid}, {name}")
            ret = self.kubeapi.mount_gpu_to_pod(self.queue[uid]["name"])
            logger.debug(f"uid:{uid} gpu mount {ret} on {node_name}")
            if (ret):
                self.queue[node_name][uid]["status"] = "START"
                self.queue[node_name][uid]["start_time"] = self.get_time()
                self.queue[node_name][uid]["end_time"] = self.get_delete_time(delta_time=self.queue[node_name][uid]["delta_time"])
                self.running[node_name] += 1
                return True
            else:
                return False
        except Exception as e:
            logger.error(e)
            return False

    """
    主邏輯控制
    1. 當排隊人數>gpu數量，就需要跑一次卸載+掛載
    2. 當排隊人數<=gpu數量，就掛載到gpu數量，且不卸載任何gpu
    """
    def run(self):
        logger.info("start time management")

        while (self.signal):
            self._add_all_node()

            for node_name in self.queue.keys():
                logger.debug(f"{node_name} queue : {self.queue[node_name]}")
                logger.debug(f"{node_name} running : {self.running[node_name]}")

            for node_name in self.queue.keys():
                uid_list = self.get_uid_list(node_name)
                if (len(uid_list) > self.max_gpu_count[node_name] and self.running[node_name] == self.max_gpu_count[node_name]):
                    self.__check(node_name, unmount=True)
                else:
                    self.__check(node_name, unmount=False)

            time.sleep(self.sleep_time_s)
        logger.info("end time management")

    def close(self):
        self.signal = False

    """
    情況1: 如果傳入time_str，就代表要取得datetime的type，因為準備要做比較或增減時間
    情況2: 如果沒傳入time_str，就代表該次是要取得時間字串
    """
    def get_time(self, time_str=None):
        try:
            if (time_str is None):
                return dt.datetime.now().strftime(self.time_format)
            else:
                return dt.datetime.strptime(time_str, self.time_format)
        except Exception as e:
            raise Exception(f"input time format error, format need is \"{self.time_format}\"")

    """
    根據dt_time共會有3種情況
    情況1: dt_time == None，需要取得當前的時間
    情況2: type(dt_time) == str，需要轉換時間格式成datetime
    情況3: type(dt_time) == datetime，直接轉換
    """
    def get_delete_time(self, dt_time=None, delta_time=None):
        if (dt_time is None):
            dt_time = self.get_time(self.get_time())
        elif (type(dt_time) == str):
            dt_time = self.get_time(dt_time)
        
        if (delta_time is None):
            return (dt_time + \
                    dt.timedelta(
                        weeks=self.default_delta_time["weeks"],
                        days=self.default_delta_time["days"],
                        hours=self.default_delta_time["hours"],
                        minutes=self.default_delta_time["minutes"],
                        seconds=self.default_delta_time["seconds"])).strftime(self.time_format)
        else:
            return (dt_time + \
                    dt.timedelta(
                        weeks=delta_time["weeks"],
                        days=delta_time["days"],
                        hours=delta_time["hours"],
                        minutes=delta_time["minutes"],
                        seconds=delta_time["seconds"])).strftime(self.time_format)


def __example():
    test_count = 10
    test_node_list = []
    test_pod_list = []
    test_delta_time = {                             # 控制掛載後的卸載時間，days可以填365以上，他會自動計算
            "weeks": 0,
            "days": 0,
            "hours": 0,
            "minutes": 5,
            "seconds": 0
        }

    for i in range(test_count):
        node_index = (i % 3) + 1
        pod_index = i
        test_node_list.append(f"node{node_index}")
        test_pod_list.append(f"pod{pod_index}")
        logger.debug(f"{test_node_list[-1]}/{test_pod_list[-1]}")

    manager = _manager()
    manager.start()

    for i in range(test_count):
        if (i == 1):
            manager.add(test_node_list[i], test_pod_list[i], delta_time=test_delta_time)
        else:
            manager.add(test_node_list[i], test_pod_list[i])


    for _ in range(50):
        time.sleep(15)
        for i in range(test_count):
            logger.debug(manager.get(test_node_list[i], test_pod_list[i]))
    manager.join()

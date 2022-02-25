import logging

logger = logging.getLogger(__name__)

import json
import threading
import datetime as dt
import time
import pkg.kubeapi
import pkg.dbapi

class _manager(threading.Thread):
    def __init__(self, node_name, sleep_time_s = 10):
        threading.Thread.__init__(self)
        self.kubeapi = pkg.kubeapi._kubeapi()
        self.node_name = node_name
        self.sleep_time_s = sleep_time_s                # 幾秒跑一次run function
        self.queue = dict()                             # 因為重開後所有pod都會重來，所以應該要是空的
        self.uid = 0                                    # 每一個申請者對應到的申請id
        self.max_gpu_count = self.__get_max_gpu_count() # GPU數量最大值
        self.running = 0                                # 正在使用的GPU數量
        self.signal = True                              # 是否要繼續執行run function
        self.time_format = "%Y/%m/%d %H:%M:%S"          # datetime format
        self.delta_time = {                             # 控制掛載後的卸載時間，days可以填365以上，他會自動計算
            "weeks": 0,
            "days": 0,
            "hours": 0,
            "minutes": 2,
            "seconds": 0
        }

        logger.debug(f"now use queue : {self.queue}")
        logger.debug(f"now use uid : {self.uid}")
        logger.debug(f"now use max_gpu_count : {self.max_gpu_count}")
        logger.debug(f"now use running : {self.running}")

    def __get_max_gpu_count(self):
        return 2

    def __get_all_name_list(self):
        all_name_list = list()
        for uid, data in self.queue.items():
            all_name_list.append(data["name"])
        return all_name_list

    def get_uid_list(self, queue=None):
        if (queue is None):
            return sorted(self.queue.keys())
        else:
            return sorted(queue.keys())

    def __get_uid_with_name(self, pod_name):
        uid_list = self.get_uid_list()
        for uid in uid_list:
            if (self.queue[uid]["name"] == pod_name):
                return uid
        raise Exception(f"pod_name: {pod_name} not in gpu queue.")

    def add(self, pod_name):
        all_name_list = self.__get_all_name_list()
        all_pod_name_list = self.kubeapi.get_all_pod().keys()
        if (pod_name in all_name_list):
            logger.info(f"pod:'{pod_name}' already exists in gpu queue, so add failed.")
        elif (not pod_name in all_pod_name_list):
            logger.info(f"pod:'{pod_name}' not in cluster or not running. so add gpu queue failed.")
            return False
        else:
            logger.info(f"pod:'{pod_name}' add gpu queue success.")
            self.queue[int(self.uid)] = {"status":"WAIT", "start_time":"", "end_time":"", "name":pod_name}
            self.uid = int(self.uid) + 1
        return True

    def remove(self, pod_name):
        try:
            uid = self.__get_uid_with_name(pod_name)
            if (self.queue[uid]["status"] == "START"):
                self.queue[uid]["status"] = "DELETE"
            else:
                self.queue[uid]["status"] = "DELETE"
                pkg.dbapi.add_log({"name":f"{self.node_name}/{pod_name}", "status":"DELETE", "start_time":self.queue[uid]["start_time"], "end_time":self.queue[uid]["end_time"]})
                del self.queue[uid]
        except Exception as e:
            logger.error(e)
        return True

    def get(self, pod_name):
        try:
            uid = self.__get_uid_with_name(pod_name)
            status = self.queue[uid]["status"]
            remain_time = "" if (len(self.queue[uid]["start_time"]) == 0) else str(self.get_time(self.queue[uid]["end_time"]) - self.get_time(self.queue[uid]["start_time"]))
            queue_index = self.get_uid_list().index(uid) - self.running + 1
            return {"gpu_status":status, "time":remain_time, "queue_index":queue_index}
        except Exception as e:
            logger.error(e)
        return {"gpu_status":"NONE", "time":"", "queue_index":""}

    """
    這邊的概念是只卸載1個pod上的GPU，所以在unmount時只要卸載到就break，並且掛載一個上去
    會這樣做主要是因為若當前排隊數量是max_gpu_count+1時，若把當前該卸載的全卸載掉，會空閒max_gpu_count-1張卡下來，所以寧願一次卸一張掛一張，讓重複執行去做掛與卸
    """
    def __check(self, uid_list=None, unmount=False):
        if (uid_list is None):
            uid_list = self.get_uid_list()

        rotation = False
    
        #先卸載自己要結束的
        for uid in uid_list:
            if (self.queue[uid]["status"] in ["DELETE"] and
                    len(self.queue[uid]["end_time"]) > 0):
                self.__unmount(uid)

        #先卸載該結束的
        if (unmount):
            for uid in uid_list:
                if (self.queue[uid]["status"] in ["START"] and 
                        len(self.queue[uid]["end_time"]) > 0 and
                        self.get_time(self.queue[uid]["end_time"]) <= self.get_time(self.get_time())):
                    self.queue[uid]["status"] = "END"
                    self.__unmount(uid)
                    break

        #掛載新的
        uid_list = self.get_uid_list()
        for uid in uid_list:
            if (self.running == self.max_gpu_count):
                break
            else:
                if (self.queue[uid]["status"] == "WAIT"):
                    if (self.__mount(uid)):
                        rotation = True
                        break
        return rotation

    def __unmount(self, uid):
        try:
            name = self.queue[uid]["name"]
            pkg.dbapi.add_log({"name":f"{self.node_name}/{pod_name}", "status":"DELETE", "start_time":self.queue[uid]["start_time"], "end_time":self.queue[uid]["end_time"]})
            del self.queue[uid]
            ret = self.kubeapi.remove_gpu_to_pod(name)
            if (ret):
                self.running -= 1
                return True
            else:
                return False
        except Exception as e:
            logger.error(e)
            logger.info(f"uid:{uid} unmount gpu failed. so restart pod")
            self.kubeapi._delete_pod(name)
            self.kubeapi._apply_pod(name)
            self.running -= 1
            return True

    def __mount(self, uid):
        if (not self.queue[uid]["status"] in ["WAIT"]):
            return True
        try:
            name = self.queue[uid]["name"]
            logger.info(f"mount uid : {uid}, {name}")
            ret = self.kubeapi.mount_gpu_to_pod(self.queue[uid]["name"])
            logger.info(f"uid:{uid} gpu mount {ret}")
            if (ret):
                self.queue[uid]["status"] = "START"
                self.queue[uid]["start_time"] = self.get_time()
                self.queue[uid]["end_time"] = self.get_delete_time()
                self.running += 1
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
            uid_list = self.get_uid_list()
            if (len(uid_list) > self.max_gpu_count):
                logger.debug("check, unmount and mount")
                self.__check(unmount=True)
            else:
                self.__check(unmount=False)

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
    def get_delete_time(self, dt_time=None):
        if (dt_time is None):
            dt_time = self.get_time(self.get_time())
        elif (type(dt_time) == str):
            dt_time = self.get_time(dt_time)
        return (dt_time + \
                dt.timedelta(
                    weeks=self.delta_time["weeks"],
                    days=self.delta_time["days"],
                    hours=self.delta_time["hours"],
                    minutes=self.delta_time["minutes"],
                    seconds=self.delta_time["seconds"])).strftime(self.time_format)

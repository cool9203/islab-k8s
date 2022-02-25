import hashlib
import time
import random

ENCODING = "utf8"
RAND_MAX = 99999
RAND_MIN = 1000

def get_hash(data):
    hash_str = f"{data} {time.time()} {random.randint(RAND_MIN, RAND_MAX)} {random.randint(RAND_MIN, RAND_MAX)}"
    md5 = hashlib.md5()
    md5.update(hash_str.encode(ENCODING))
    md5_str = md5.hexdigest()
    return md5_str


def data_encode(data):
    return data

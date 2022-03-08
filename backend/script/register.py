from pathlib import Path
import sys
sys.path.insert(0, str(Path("../").resolve()))
sys.path.insert(0, str(Path("./").resolve()))

import pkg.dbapi

uid = input("register uid:")
password = input("register password:")
name = input("register name:")
print("register result : ", pkg.dbapi.register(uid, password, name))


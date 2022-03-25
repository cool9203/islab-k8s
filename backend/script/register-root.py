from pathlib import Path
import sys
sys.path.insert(0, str(Path("../").resolve()))
sys.path.insert(0, str(Path("./").resolve()))

import pkg.dbapi
print("register-root result : ", pkg.dbapi.register("islab", "islabs102a", "islab", 0))


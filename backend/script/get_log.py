from pathlib import Path
import sys
sys.path.insert(0, str(Path("../").resolve()))
sys.path.insert(0, str(Path("./").resolve()))

import pkg.dbapi

print(pkg.dbapi.db.select(f"SELECT * FROM log"))

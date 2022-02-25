import sys
import os
sys.path.insert(0, os.environ["PWD"])


def test_base():
    assert 2==2

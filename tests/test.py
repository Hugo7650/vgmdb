import time
import random
from vgmdb import VGMdb


def test():
    for _ in range(100):
        id = random.randint(1, 131900)
        result = VGMdb.get_album(id)
        print(id, result)
        time.sleep(1)

import unittest
import random
from vgmdb import VGMdb


class Test(unittest.TestCase):
    def test(self):
        for i in range(100):
            id = random.randint(1, 131900)
            result = VGMdb.get_album(id)
            print(id, result)


if __name__ == "__main__":
    unittest.main()

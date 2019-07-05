import Mapping

class LinearMapping(Mapping):
    table = {}

    def __init__(self, v_address):
        for i in range(1024):
            self.table[i] = (0,0)


    def map(self):
        pass
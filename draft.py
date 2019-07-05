

class PhysicalMemory(object):
    
    def __init__(self, memory_size, page_size):
        super(PhysicalMemory, self).__init__()
        self.memory_size = memory_size
        self.page_size = page_size
        self.address_table = {}
        for address in range(0, memory_size, page_size):
            self.address_table[address] = False

    def get(self):
        for address, in_use in  self.address_table.items():
            if not in_use: 
                return address
    
    def put(self, mem_address):
        self.address_table[mem_address] = True
    
    def evict(self, mem_address):
        self.address_table[mem_address] = False

class LinearMapping(object):

    def __init__(self, memory_size=2147483648, page_size=4096):
      super(LinearMapping, self).__init__()
      self.physicalMemory = PhysicalMemory(memory_size, page_size)
      self.page_table = {}

    def map(self, virtual_address):
        frame_id = virtual_address >> 12
        offset = int(bin(virtual_address)[2 + 20:], 2)

        hw_address, frame_id, n_pagefaults = 0, 0, 0 # tmp values
        if frame_id in self.page_table:
            hw_begin = self.page_table[frame_id]
            
        else:
            n_pagefaults = 1
            hw_begin = self.physicalMemory.get()
            self.physicalMemory.put(hw_begin)
            self.page_table[frame_id] = hw_begin
        
        hw_address = hw_begin + offset
        return hw_address, frame_id, n_pagefaults

class HierarchicalMapping(object):

    def __init__(self, memory_size=2147483648, page_size=4096):
      super(HierarchicalMapping, self).__init__()
      self.PT1_table = {}
      self.PT2_table = LinearMapping()

    def map(self, virtual_address):
        PT1 = virtual_address >> 22
        PT2 = int(bin(virtual_address >> 12)[2 + 10:], 2)
        offset = int(bin(virtual_address)[2 + 20:], 2)
        
        pagefault = 0
        if PT1 not in self.PT1_table: # TODO(to check if it is correct)
            pagefault += 1
            self.PT1_table[PT1] = PT2

        hw_address, frame_id, n_pagefaults = self.PT2_table.map(virtual_address)
        return hw_address + offset, frame_id, n_pagefaults + pagefault

class InvertedMapping(object):

    def __init__(self, memory_size=8589934592, page_size=4096):
      super(HierarchicalMapping, self).__init__()
      self.physicalMemory = PhysicalMemory(memory_size, page_size)
    
    def map(self, virtual_address):
        pass
